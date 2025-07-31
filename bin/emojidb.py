#!/usr/bin/env python
#
# autor: Ethan Liu
#
# all about emoji
# since all we need for emoji are only a few files
# using the whole repo is kinda heavy, download individual file instead
#
# refs:
# https://github.com/unicode-org/cldr-json
# https://www.unicode.org/Public/emoji/

import argparse
import sys, os
import json
import urllib3, shutil
import re, sqlite3
from tqdm import tqdm
from lib.util import db_get_one, trim

# Global Variables

DB_PATH = ''


EMOJI_DATA_LIST = {
	"emoji-data.txt": "https://www.unicode.org/Public/17.0.0/ucd/emoji/emoji-data.txt",
	"emoji-variation-sequences.txt": "https://www.unicode.org/Public/17.0.0/ucd/emoji/emoji-variation-sequences.txt",

	"emoji-sequences.txt": "https://www.unicode.org/Public/emoji/17.0/emoji-sequences.txt",
	"emoji-zwj-sequences.txt": "https://www.unicode.org/Public/emoji/17.0/emoji-zwj-sequences.txt",

	"annotations_en.json": "https://github.com/unicode-org/cldr-json/raw/main/cldr-json/cldr-annotations-full/annotations/en/annotations.json",
	"annotations_hant.json": "https://github.com/unicode-org/cldr-json/raw/main/cldr-json/cldr-annotations-full/annotations/zh-Hant/annotations.json",
	"annotations_hans.json": "https://github.com/unicode-org/cldr-json/raw/main/cldr-json/cldr-annotations-full/annotations/zh/annotations.json",

	"derived_en.json": "https://github.com/unicode-org/cldr-json/raw/main/cldr-json/cldr-annotations-derived-full/annotationsDerived/en/annotations.json",
	"derived_hant.json": "https://github.com/unicode-org/cldr-json/raw/main/cldr-json/cldr-annotations-derived-full/annotationsDerived/zh-Hant/annotations.json",
	"derived_hans.json": "https://github.com/unicode-org/cldr-json/raw/main/cldr-json/cldr-annotations-derived-full/annotationsDerived/zh/annotations.json",
}

EMOTICONS_PATH = os.path.abspath(os.path.join(os.getcwd(), os.pardir, 'lexicon/emoticons.json'))
COMMON_WORDS_LIST = ['skin tone', '膚色', '肤色']

# Unicode special characters
EMOJI_VS = "0000FE0F" # Variation Selector for Emoji Presentation
ZWJ = "0000200D"      # Zero Width Joiner

# Skin tone modifier characters (Fitzpatrick scale)
SKIN_TONE_MODIFIERS_HEX = {
	"0001F3FB", "0001F3FC", "0001F3FD", "0001F3FE", "0001F3FF"
}

# Reversed mapping name to id
# https://www.unicode.org/reports/tr51
EMOJI_CATEGORY_MAP = {
	'Emoji': 1,
	'Basic_Emoji': 2,
	'Emoji_Component': 3,
	'Emoji_Keycap_Sequence': 4,
	'Emoji_Modifier_Base': 5,
	'Emoji_Modifier': 6,
	'Emoji_Presentation': 7,
	'Extended_Pictographic': 8,
	'RGI_Emoji_Flag_Sequence': 9,
	'RGI_Emoji_Modifier_Sequence': 10,
	'RGI_Emoji_Tag_Sequence': 11,
	'RGI_Emoji_ZWJ_Sequence': 12,
}

def _collect_keywords(string_list, prefix):
	return [item.replace(prefix, '').strip() for item in string_list]

def emojilized(hexString):
	if hexString == "" or hexString is None:
		return ""

	try:
		# Pad each code point to 8 digits before joining to form the \UXXXXXXXX escape sequence
		# This handles cases where char_to_long_hex might produce fewer than 8 digits for some reason.
		codes_list = hexString.split(' ')
		escaped_codes = []
		for c in codes_list:
			# Ensure it's 8 digits by converting to int and formatting as 08X
			try:
				escaped_codes.append(f"\\U{int(c, 16):08X}")
			except ValueError:
				# If a part isn't a valid hex, skip or handle error
				print(f"Warning: Invalid hex code part '{c}' in '{hexString}'")
				return "" # Return empty or handle as error

		codes = "".join(escaped_codes)
		return codes.encode('latin1').decode('unicode-escape')

	except Exception as e:
		print(f"Invalid code or decoding error for '{hexString}': {e}")
	return ""

# Pads a Unicode hexadecimal string to 8 digits with leading zeros.
def pad_hex_to_8_digits(hex_code):
	# Ensure it's uppercase and remove any 'U+' or '0x' prefixes if present
	hex_code = hex_code.upper().replace('U+', '').replace('0X', '')
	nodes = []
	for node in hex_code.split():
		if node:
			# Pad with leading zeros to 8 characters
			# Use X for uppercase hex
			part = f"{int(node, 16):08X}"
			# part = hex_code.zfill(8)
			nodes.append(part)
	return ' '.join(nodes)

# Converts a character (like an emoji) into its long hexadecimal Unicode representation,
# with each code point formatted as 8 digits and joined by a single space.
# Returns None if conversion fails.
def char_to_long_hex(char):
	if not isinstance(char, str):
		return None
	codes_raw = char.encode('unicode-escape').decode('ascii')
	# Split by '\U' or '\x' (case-insensitive) and filter out empty strings
	code_parts = list(filter(None, re.split(r'\\U|\\x', codes_raw, flags=re.IGNORECASE)))

	formatted_codes = []
	for code in code_parts:
		try:
			formatted_codes.append(pad_hex_to_8_digits(code))
		except ValueError:
			return None

	return ' '.join(formatted_codes).upper()

# Removes all standard Unicode skin tone modifiers and VS16
# from a space-separated string of hex Unicode code points.
# Also handles extra spaces.
def remove_skin_tone(hex_codes_string, remove_vs = False):
	if hex_codes_string is None:
		return None
	elif hex_codes_string == EMOJI_VS:
		return None

	to_remove = SKIN_TONE_MODIFIERS_HEX
	if remove_vs is True:
		# Combine skin tones and VS16 into one set for removal
		to_remove = SKIN_TONE_MODIFIERS_HEX.union({EMOJI_VS})

	pattern = r'\b(' + '|'.join(re.escape(s) for s in to_remove) + r')\b'
	cleaned_string = re.sub(pattern, "", hex_codes_string)
	cleaned_node = cleaned_string.split()

	if len(cleaned_node) == 1:
		if EMOJI_VS in cleaned_string:
			# print(cleaned_node)
			# print(f"xxx: {hex_codes_string} vs {cleaned_string}")
			return None

	# Normalize whitespace: split by any whitespace, filter out empty, join with single space, strip ends
	final_string = ' '.join(cleaned_node).strip()

	if final_string == "0001FE0F" or final_string == "1FE0F":
		print("xxxx???")
		return None

	return final_string

def create_database():
	if os.path.isfile(DB_PATH):
		os.remove(DB_PATH)

	db = sqlite3.connect(DB_PATH)
	cursor = db.cursor()

	cursor.execute("CREATE TABLE keydef (`key` VARCHAR(255) UNIQUE NOT NULL)")
	cursor.execute("CREATE TABLE chardef (`char` VARCHAR(255) UNIQUE NOT NULL, `weight` INTEGER DEFAULT 0)")
	cursor.execute("CREATE TABLE entry (`keydef_id` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL, UNIQUE(`keydef_id`, `chardef_id`) ON CONFLICT IGNORE)")
	cursor.execute("CREATE TABLE category (`chardef_id` INTEGER NOT NULL, `category_id` INTEGER DEFAULT 0)")

	db.commit()
	db.close()

# Create the emoji database base on emoji-data.txt and zwj
def apply_emojis(basedir):
	db = sqlite3.connect(DB_PATH)
	cursor = db.cursor()

	path1 = os.path.join(basedir, "emoji-data.txt")
	path2 = os.path.join(basedir, "emoji-sequences.txt")
	path3 = os.path.join(basedir, "emoji-variation-sequences.txt")
	path4 = os.path.join(basedir, "emoji-zwj-sequences.txt")

	import_from_emoji_data(cursor, path1)
	import_from_emoji_data(cursor, path2)
	# # import_from_emoji_data(cursor, path3)
	import_from_emoji_data(cursor, path4)

	db.commit()
	db.close()

# 	# Regex:
# 	# ^\s* - Start of line, optional leading whitespace
# 	# ([0-9A-F\s]+)            - Group 1: Hex codes and spaces (e.g., "1FAF1 1F3FE 200D 1FAF2 1F3FF")
# 	# \s*;\s* - First semicolon, with optional surrounding whitespace
# 	# ([^;]+?)                 - Group 2: Category (e.g., "RGI_Emoji_ZWJ_Sequence"), non-greedy match of anything not a semicolon
# 	# \s*;\s* - Second semicolon, with optional surrounding whitespace
# 	# .* - Match the rest of the line (which we ignore)
# 	# $                        - End of line
# 	pattern = re.compile(r'^\s*([0-9A-F\s]+)\s*;\s*([^;]+?)\s*;\s*.*$')

def import_from_emoji_data(cursor, file_path):
	# Regex to capture the code hex range and the category, ignoring comments
	# pattern = re.compile(r'^\s*([0-9A-F]+(?:..[0-9A-F]+)?)\s*;\s*([A-Za-z_]+)(?:.*#.*)?$')

	filename = os.path.basename(file_path)

	insert_chardef_query = "INSERT OR IGNORE INTO chardef (char) VALUES (:char)"
	select_chardef_query = "SELECT rowid FROM chardef WHERE char = :char LIMIT 1"
	insert_category_query = "INSERT OR IGNORE INTO category (chardef_id, category_id) VALUES (:chardef_id, :category_id)"

	cursor.execute("BEGIN TRANSACTION")

	with open(file_path, 'r', encoding='utf-8') as f:
		# for line in f:
		for line in tqdm(f, desc = f"{filename}", unit_scale = True, ascii = True):
			# line = line.strip()
			if "<reserved" in line:
				continue

			line = trim(line, '#')
			if not line:
				continue

			# match = pattern.match(line)
			# if not match:
			# 	print(f"missing: {line}")
			# 	continue
			# hex_code = match.group(1)
			# category = match.group(2)

			# Simple and more robust than re
			nodes = line.split(';')
			hex_code_raw = nodes[0].strip() if nodes[0] else ""
			category = nodes[1].strip() if nodes[1] else ""

			# TODO: variations
			if category == "text style":
				continue
			if category == "emoji style":
				continue
			if category == 'Emoji_Modifier':
				continue

			category_id = EMOJI_CATEGORY_MAP.get(category) if EMOJI_CATEGORY_MAP.get(category) else None

			if not category_id:
				print(f"{category} not exists")
				sys.exit(0)

			if ".." in hex_code_raw:
				emoji_block = hex_code_raw.split('..')
				begin = int(emoji_block[0], 16)
				end = int(emoji_block[1], 16) if len(emoji_block) > 1 and emoji_block[1] else begin

				for codepoint in range(begin, end + 1):
					hex_code = f"{codepoint:08X}"  # or :08X for 8 digits

					cursor.execute(insert_chardef_query, {'char': hex_code})
					chardef_id = db_get_one(cursor, select_chardef_query, {'char': hex_code})
					cursor.execute(insert_category_query, {'chardef_id': chardef_id, 'category_id': category_id})
			else:
				hex_code = pad_hex_to_8_digits(hex_code_raw)
				hex_code = remove_skin_tone(hex_code)
				if not hex_code:
					continue

				# print(f"===> \n{hex_code}\n{hex_code_raw}")
				cursor.execute(insert_chardef_query, {'char': hex_code})
				chardef_id = db_get_one(cursor, select_chardef_query, {'char': hex_code})
				cursor.execute(insert_category_query, {'chardef_id': chardef_id, 'category_id': category_id})

	cursor.execute("COMMIT TRANSACTION")

def apply_annotations(data_dir):
	db = sqlite3.connect(DB_PATH)
	cursor = db.cursor()

	for lang in ["en", "hant", "hans"]:
		path1 = os.path.join(data_dir, f"annotations_{lang}.json")
		path2 = os.path.join(data_dir, f"derived_{lang}.json")
		apply_annotation_data(cursor, path1)
		apply_annotation_data(cursor, path2)

	db.commit()
	db.close()

# Parses CLDR annotation data
def apply_annotation_data(cursor, path):
	filename = os.path.basename(path)
	file = open(path, 'r')
	data = json.load(file)
	file.close()

	node = None
	if 'annotationsDerived' in data:
		node = data['annotationsDerived']['annotations']
	elif 'annotations' in data:
		node = data['annotations']['annotations']
	else:
		print(f"Node not found in CLDR file: {path}")
		return

	insert_chardef_query = "INSERT OR IGNORE INTO chardef (char) VALUES (:char)"
	select_chardef_query = "SELECT rowid FROM chardef WHERE char = :char LIMIT 1"

	insert_keydef_query = "INSERT OR IGNORE INTO keydef (key) VALUES (:key)"
	select_keydef_query = "SELECT rowid FROM keydef WHERE key = :key LIMIT 1"

	insert_entry_query = "INSERT OR IGNORE INTO entry (keydef_id, chardef_id) VALUES (:kid, :cid)"

	cursor.execute("BEGIN TRANSACTION")

	for emoji_char, annotations in tqdm(node.items(), unit = filename, ascii = True):
		hex_code_raw = char_to_long_hex(emoji_char)
		hex_code = remove_skin_tone(hex_code_raw)

		if not hex_code:
			# tqdm.write(f"[annotation][invalid] ignore {emoji_char}")
			continue

		chardef_id = db_get_one(cursor, select_chardef_query, {'char': hex_code})
		if not chardef_id:
			# tqdm.write(f"[annotation][new] {emoji_char} {hex_code_raw} | {hex_code}")
			cursor.execute(insert_chardef_query, {'char': hex_code})
			chardef_id = db_get_one(cursor, select_chardef_query, {'char': hex_code})
			# continue

		keywords = []
		if 'default' in annotations:
			keywords = annotations['default']

		if keywords == ['flag']:
			keywords = _collect_keywords(annotations.get('tts', []), 'flag: ')
			keywords.append('flag')
			keywords.append('旗')
		elif keywords == ['keycap']:
			keywords = _collect_keywords(annotations.get('tts', []), 'keycap: ')
			keywords.append('keycap')

		# Handle keywords and insert into DB
		for keyword in keywords:
			_keyword = keyword.strip()
			if any(words in _keyword for words in COMMON_WORDS_LIST):
				# tqdm.write(f"skip common keyword: {emoji_char} {_keyword}")
				continue

			cursor.execute(insert_keydef_query, {'key': _keyword})
			keydef_id = db_get_one(cursor, select_keydef_query, {'key': _keyword})

			if chardef_id and keydef_id:
				cursor.execute(insert_entry_query, {'kid': keydef_id, 'cid': chardef_id})

	cursor.execute("COMMIT TRANSACTION")

def apply_emoticons():
	file = open(EMOTICONS_PATH, 'r')
	data = json.load(file)
	file.close()

	db = sqlite3.connect(DB_PATH)
	cursor = db.cursor()

	cursor.execute("BEGIN TRANSACTION")

	for emoji, emoticons in data.get("emoticons", {}).items():
		codes = char_to_long_hex(emoji)
		codes = remove_skin_tone(codes)

		if not codes:
			continue

		if codes is None or codes == "":
			# print(f"Skipping emoticon '{emoji}' due to invalid or empty hex code after processing.")
			continue

		chardef_id = db_get_one(cursor, "SELECT rowid FROM `chardef` WHERE char = :char LIMIT 1", {'char': codes})
		if not chardef_id:
			cursor.execute("INSERT OR IGNORE INTO chardef (char) VALUES (:char)", {'char': codes})
			chardef_id = db_get_one(cursor, "SELECT rowid FROM `chardef` WHERE char = :char LIMIT 1", {'char': codes})
			if not chardef_id:
				# print(f"Failed to add emoticon emoji to chardef: '{emoji}' (hex: {codes})")
				continue

		for keyword in emoticons:
			cursor.execute("INSERT OR IGNORE INTO keydef (key) VALUES (:key)", {'key': keyword})
			keydef_id = db_get_one(cursor, "SELECT rowid FROM keydef WHERE key = :key LIMIT 1", {'key': keyword})
			if keydef_id:
				cursor.execute("INSERT OR IGNORE INTO entry (keydef_id, chardef_id) VALUES (:kid, :cid)", {'kid': keydef_id, 'cid': chardef_id})

	cursor.execute("COMMIT TRANSACTION")

	db.commit()
	db.close()

def apply_ranking():
	# This function also uses EMOTICONS_PATH.
	# Ensure the `remove_skin_tone` call here is also updated.
	file = open(EMOTICONS_PATH, 'r') # Assuming EMOTICONS_PATH is defined and correct
	data = json.load(file)
	file.close()

	db = sqlite3.connect(DB_PATH)
	cursor = db.cursor()

	cursor.execute("BEGIN TRANSACTION")

	for index, items in enumerate(reversed(data.get("ranking", []))):
		weight = 10000 + (100 * index)
		for item in items[::-1]:
			weight += 1
			code = char_to_long_hex(item)
			code = remove_skin_tone(code) # Use the updated cleaning function

			if code is None or code == "":
				# print(f"Skipping ranking item '{item}' due to invalid or empty hex code after processing.")
				continue

			cursor.execute("UPDATE `chardef` SET weight = :weight WHERE char = :code", {'code': code, 'weight': weight})

	cursor.execute("COMMIT TRANSACTION")

	db.commit()
	db.close()

def test(phrase, dbPath):
	if not os.path.isfile(dbPath):
		sys.exit("Error: Database file not found for test.")

	db = sqlite3.connect(dbPath)
	cursor = db.cursor()

	print(f"\n--- Searching for phrase: '{phrase}' ---")
	if phrase == 'emoji':
		cursor.execute("SELECT char, weight FROM chardef ORDER BY RANDOM() LIMIT 100")
		result = cursor.fetchall()

		if not result:
			print("No emojis found in database.")
			return

		for item in result:
			emoji = emojilized(item[0])
			print(f"{emoji} (Weight: {item[1]})", end = ' ')
		print('\n')

	elif phrase == 'ranking':
		cursor.execute("SELECT char FROM `chardef` WHERE weight > 0 ORDER BY weight DESC")
		result = cursor.fetchall()
		for item in result:
			emoji = emojilized(item[0])
			print(emoji, end = ' ')
		print('')

	elif phrase == 'zwj':
		zwj_id = EMOJI_CATEGORY_MAP['RGI_Emoji_ZWJ_Sequence']
		query = f"""
		SELECT DISTINCT chardef.char
		FROM chardef, category
		WHERE chardef.rowid = category.chardef_id
			AND category.category_id = {zwj_id}
		"""
		cursor.execute(query)
		result = cursor.fetchall()

		if not result:
			print(f"No result for phrase: '{phrase}'")
			return

		for item in result:
			# print(f"{emojilized(item[0])}", end=' ')
			print(f"{emojilized(item[0])}: {item[0]}")

	else:
		query = f"""
		SELECT DISTINCT chardef.char, keydef.key, chardef.weight
		FROM keydef, chardef, entry
		WHERE (keydef.key LIKE ? OR keydef.key LIKE ? OR keydef.key LIKE ? OR keydef.key LIKE ?)
			AND keydef.ROWID = entry.keydef_id
			AND chardef.ROWID = entry.chardef_id
		ORDER BY chardef.weight DESC, keydef.key ASC
		LIMIT 50
		"""
		cursor.execute(query, [phrase, f'% {phrase} %', f'%{phrase} %', f'% {phrase}%'])
		result = cursor.fetchall()

		if not result:
			print(f"No result for phrase: '{phrase}'")
			return

		for item in result:
			print(f"{emojilized(item[0])}\tKeyword: {item[1]}\tWeight: {item[2]}")

	db.close()

def update_resources(basedir):
	os.makedirs(basedir, exist_ok=True)
	pool = urllib3.PoolManager()
	for filename, url in EMOJI_DATA_LIST.items():
		path = os.path.join(basedir, filename)
		print(f"Download: {path}")
		try:
			with pool.request('GET', url, preload_content=False) as res, open(path, 'wb') as f:
				shutil.copyfileobj(res, f)
			res.release_conn()
		except Exception as e:
			print(f"Error downloading {url}: {e}")
			if os.path.exists(path):
				os.remove(path)
	print("Update finished")


def main():
	arg_reader = argparse.ArgumentParser(description='emoji.db Utility')
	arg_reader.add_argument('--update', action=argparse.BooleanOptionalAction, help='Update CLDR and Unicode emoji json/txt files (into --dir)')
	arg_reader.add_argument('--run', action=argparse.BooleanOptionalAction, help='Run import (into --output DB file) and generate Swift JSON')
	arg_reader.add_argument('-test', type = str, help='Test keyword or "emoji" for random, "modifiable" for generated lists')
	arg_reader.add_argument('-d', '--dir', type = str, help='The directory path to store/read cldr-json and unicode-emoji files')
	arg_reader.add_argument('-o', '--output', type = str, help='The file path of emoji.db')

	args = arg_reader.parse_args()

	if args.update:
		if not args.dir or not os.path.exists(args.dir):
			print(f"Error: Directory '{args.dir}' not found. Please provide a valid directory for cldr-json files.")
			sys.exit(1)
		update_resources(args.dir)
		sys.exit(0)

	if args.run:
		if not args.output:
			print("Error: Output database file path (-o/--output) is required for --run.")
			sys.exit(1)

		if not args.dir or not os.path.exists(args.dir):
			print(f"Error: Directory '{args.dir}' not found. Please provide a valid directory for cldr-json files.")
			sys.exit(1)

		if not args.output:
			print("Error: Output database file path (-o/--output) is required for --run.")
			sys.exit(1)

		global DB_PATH
		DB_PATH = args.output

		create_database()

		apply_emojis(args.dir)
		apply_annotations(args.dir)

		apply_emoticons()
		apply_ranking()

		sys.exit(0)

	if args.test:
		if not args.output:
			print("Error: Output database file path (-o/--output) is required for --run.")
			sys.exit(1)
		test(args.test, args.output)


	if not any(vars(args).values()):
		arg_reader.print_help()
		sys.exit(0)

if __name__ == "__main__":
	main()