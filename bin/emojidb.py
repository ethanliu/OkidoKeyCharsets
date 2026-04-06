#!/usr/bin/env uv run
#
# autor: Ethan Liu
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
from lib.util import db_get_one
from country import get_country_data
# import random

# Global Variables

EMOTICONS_PATH = os.path.join(os.getcwd(), 'lexicon', 'emoticons.json')
COUNTRY_CSV_PATH = os.path.join(os.getcwd(), 'misc', 'countries.csv')

EMOJI_DATA_LIST = {
    "emoji-test.txt": "https://www.unicode.org/Public/17.0.0/emoji/emoji-test.txt",
    "annotations_en.json": "https://github.com/unicode-org/cldr-json/raw/main/cldr-json/cldr-annotations-full/annotations/en/annotations.json",
    "annotations_hant.json": "https://github.com/unicode-org/cldr-json/raw/main/cldr-json/cldr-annotations-full/annotations/zh-Hant/annotations.json",
    "annotations_hans.json": "https://github.com/unicode-org/cldr-json/raw/main/cldr-json/cldr-annotations-full/annotations/zh/annotations.json",
}

COMMON_WORDS_LIST = ['skin tone', '膚色', '肤色']

DB_PATH = ''
EMOJI_VS = "0000FE0F"
ZWJ = "0000200D"

# 0001F3FB	Type 1–2 (Pale/Fair)	1
# 0001F3FC	Type 3 (Cream White)	2
# 0001F3FD	Type 4 (Moderate Brown)	3
# 0001F3FE	Type 5 (Dark Brown)	4
# 0001F3FF	Type 6 (Deeply Pigmented)	5

SKIN_TONE_MAP = {
    "0001F3FB": 1, "0001F3FC": 2, "0001F3FD": 3, "0001F3FE": 4, "0001F3FF": 5
}

# --- Utility Functions ---

def pad_hex_to_8_digits(hex_code):
    hex_code = hex_code.upper().replace('U+', '').replace('0X', '')
    return ' '.join([f"{int(node, 16):08X}" for node in hex_code.split() if node])

def emojilized(hex_string):
    if not hex_string: return ""
    try:
        codes = "".join([f"\\U{int(c, 16):08X}" for c in hex_string.split()])
        return codes.encode('latin1').decode('unicode-escape')
    except: return ""

def analyze_emoji(hex_codes_string):
    nodes = hex_codes_string.split()

    # Extract skin tones
    found_tones = [SKIN_TONE_MAP[n] for n in nodes if n in SKIN_TONE_MAP]

    # Metadata flags
    is_skin = 1 if found_tones else 0
    is_zwj = 1 if ZWJ in nodes else 0
    has_vs = 1 if EMOJI_VS in nodes else 0

    tone1 = found_tones[0] if len(found_tones) > 0 else 0
    tone2 = found_tones[1] if len(found_tones) > 1 else 0

    # We remove Skin Tones and VS to find the "Base" version
    parent_nodes = [n for n in nodes if n not in SKIN_TONE_MAP and n != EMOJI_VS]

    # Clean up ZWJ artifacts (remove double ZWJs or trailing ZWJs)
    final_parent_nodes = []
    for node in parent_nodes:
        if node == ZWJ and (not final_parent_nodes or final_parent_nodes[-1] == ZWJ):
            continue
        final_parent_nodes.append(node)

    # If the sequence ended in a ZWJ after stripping, remove it
    if final_parent_nodes and final_parent_nodes[-1] == ZWJ:
        final_parent_nodes.pop()

    parent_hex = ' '.join(final_parent_nodes)

    # If the parent is identical to original, set to None
    if parent_hex == hex_codes_string:
        parent_hex = None

    return is_skin, is_zwj, has_vs, tone1, tone2, parent_hex

def _collect_keywords(string_list, prefix):
    return [item.replace(prefix, '').strip() for item in string_list]

def normalize_emoji_hex(char):
    # Remove Variation Selectors (FE00 through FE0F)
    # These are what differentiate fully-qualified from minimally-qualified
    clean_char = re.sub(r'[\ufe00-\ufe0f]', '', char)
    # Convert to hex sequence
    return ' '.join(f"{ord(c):08X}" for c in clean_char)
    # return ' '.join(f"{ord(c):08X}" for c in char)

# --- Database Core ---

def create_database():
    if os.path.isfile(DB_PATH): os.remove(DB_PATH)
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()

    # Added metadata columns to chardef
    cursor.execute("""
        CREATE TABLE chardef (
            `char` VARCHAR(255) UNIQUE NOT NULL,
            `is_skin_tone` INTEGER DEFAULT 0,
            `is_zwj` INTEGER DEFAULT 0,
            `has_vs` INTEGER DEFAULT 0,
            `skin_tone_1` INTEGER DEFAULT 0,
            `skin_tone_2` INTEGER DEFAULT 0,
            `weight` INTEGER DEFAULT 0,
            `parent_hex` VARCHAR(255)
        )
    """)

    cursor.execute("CREATE TABLE keydef (`key` VARCHAR(255) UNIQUE NOT NULL)")
    cursor.execute("CREATE TABLE entry (`keydef_id` INTEGER, `chardef_id` INTEGER, UNIQUE(`keydef_id`, `chardef_id`))")

    cursor.execute("CREATE INDEX idx_emoji_ranking ON chardef(is_skin_tone, weight)")
    cursor.execute("CREATE INDEX idx_emoji_lookup ON chardef(skin_tone_1, skin_tone_2, weight)")
    cursor.execute("CREATE INDEX idx_parent_lookup ON chardef(weight, parent_hex)")
    cursor.execute("CREATE INDEX idx_entry_lookup ON entry(keydef_id, chardef_id)")
    cursor.execute("CREATE INDEX idx_entry_reverse_lookup ON entry(chardef_id, keydef_id)")

    db.commit()
    db.close()

def import_from_emoji_test(cursor, file_path):
    filename = os.path.basename(file_path)
    current_group = ""
    current_subgroup = ""

    cursor.execute("BEGIN TRANSACTION")

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in tqdm(f, desc=f"Importing {filename}", ascii=True):
            line = line.strip()

            # 1. Track Groups/Subgroups for metadata
            if line.startswith("# group:"):
                current_group = line.split(":", 1)[1].strip()
                continue
            if line.startswith("# subgroup:"):
                current_subgroup = line.split(":", 1)[1].strip()
                continue

            # 2. Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            # 3. Parse Data Line
            # Example: 1F44B 1F3FB ; fully-qualified # 👋🏻 E1.0 waving hand: light skin tone
            parts = line.split(";")
            if len(parts) < 2: continue

            hex_raw = parts[0].strip()
            status = parts[1].split("#")[0].strip()

            # We usually only want 'fully-qualified' for a clean database
            if status != "fully-qualified":
                continue

            # 4. Standardize Hex
            h_code = pad_hex_to_8_digits(hex_raw)

            # 5. Extract Skin Tones and Parent (using the logic we built)
            is_skin, is_zwj, has_vs, tone1, tone2, parent = analyze_emoji(h_code)

            # 6. Insert into DB
            cursor.execute("""
                INSERT OR IGNORE INTO chardef
                (char, is_skin_tone, is_zwj, has_vs, skin_tone_1, skin_tone_2, parent_hex)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (h_code, is_skin, is_zwj, has_vs, tone1, tone2, parent))

    cursor.execute("COMMIT TRANSACTION")

# Create the emoji database base on emoji-data.txt and zwj
def apply_emojis(basedir):
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()

    path = os.path.join(basedir, "emoji-test.txt")
    import_from_emoji_test(cursor, path)

    db.commit()
    db.close()

def apply_annotations(data_dir):
    global countries
    countries = get_country_data()

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

    # insert_chardef_query = "INSERT OR IGNORE INTO chardef (char) VALUES (:char)"
    # select_chardef_query = "SELECT rowid FROM chardef WHERE char = :char LIMIT 1"

    # annotations_en.json is "Minimal"
    select_chardef_query = f"SELECT rowid FROM chardef WHERE REPLACE(char, ' {EMOJI_VS}', '') = :char LIMIT 1"

    insert_keydef_query = "INSERT OR IGNORE INTO keydef (key) VALUES (:key)"
    select_keydef_query = "SELECT rowid FROM keydef WHERE key = :key LIMIT 1"

    insert_entry_query = "INSERT OR IGNORE INTO entry (keydef_id, chardef_id) VALUES (:kid, :cid)"

    cursor.execute("BEGIN TRANSACTION")

    for emoji_char, annotations in tqdm(node.items(), unit = filename, ascii = True, unit_scale=True):
        # hex_code_raw = char_to_long_hex(emoji_char)
        # hex_code = remove_skin_tone(hex_code_raw)
        # hex_code = char_to_long_hex(emoji_char)
        hex_code = normalize_emoji_hex(emoji_char)

        if not hex_code:
            # tqdm.write(f"[annotation][invalid] ignore {emoji_char}")
            continue

        chardef_id = db_get_one(cursor, select_chardef_query, {'char': hex_code})
        if not chardef_id:
            # tqdm.write(f"[annotation][new] {emoji_char} | {hex_code}")
            continue

        # tqdm.write(f"[annotation][{chardef_id}] {emoji_char} | {hex_code}")
        keywords = []
        if 'default' in annotations:
            keywords = annotations['default']

        if keywords == ['flag']:
            keywords = _collect_keywords(annotations.get('tts', []), 'flag: ')

            countryKey = keywords[0].lower().replace(" ", "_")
            info = countries.get(countryKey, {})
            if info:
                # print(emoji_char, info["alpha2"], info["hant"])
                # keywords.append(info["alpha2"])
                keywords.append(info["code"])
                keywords.append(info["hant"])
                keywords.append(info["hans"])
            # else:
            #     print("404:", emoji_char, countryKey, keywords[0])

            keywords.append('flag')
            keywords.append('旗')
            # print(emoji_char, keywords)
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


def apply_ranking():
    file = open(EMOTICONS_PATH, 'r')
    data = json.load(file)
    file.close()

    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()

    cursor.execute("BEGIN TRANSACTION")

    for index, items in enumerate(reversed(data.get("ranking", []))):
        weight = 10000 + (100 * index)
        for item in items[::-1]:
            weight += 1
            code = normalize_emoji_hex(item)

            if code is None or code == "":
                # print(f"Skipping ranking item '{item}' due to invalid or empty hex code after processing.")
                continue

            cursor.execute(f"UPDATE `chardef` SET weight = :weight WHERE REPLACE(char, ' {EMOJI_VS}', '') = :code", {'code': code, 'weight': weight})

    cursor.execute("COMMIT TRANSACTION")

    db.commit()
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


def test_fetch_random_emoji_with_keywords(cursor):
    """Fetches a random emoji and all its associated keywords."""
    print("--- Test: Random Emoji -> Keywords ---")

    # 1. Get a random chardef_id and its character string
    cursor.execute("SELECT rowid, `char` FROM chardef ORDER BY RANDOM() LIMIT 1")
    result = cursor.fetchone()

    if not result:
        print("Database is empty.")
        return

    char_id, hex_code = result
    emoji = emojilized(hex_code)

    # 2. Fetch all keys associated with this chardef
    cursor.execute("""
        SELECT k.`key`
        FROM keydef k
        JOIN entry e ON k.rowid = e.keydef_id
        WHERE e.chardef_id = ?
    """, (char_id,))

    keywords = [row[0] for row in cursor.fetchall()]

    print(f"Emoji Hex: {hex_code}")
    print(f"Emoji Glyph: {emoji}")
    print(f"Keywords: {', '.join(keywords) if keywords else 'None found'}")
    print("\n")

def test_fetch_random_keyword_with_emojis(cursor):
    """Fetches a random keyword and all emojis associated with it."""
    print("--- Test: Random Keyword -> Emojis ---")

    # 1. Get a random keyword
    cursor.execute("SELECT rowid, `key` FROM keydef ORDER BY RANDOM() LIMIT 1")
    result = cursor.fetchone()

    if not result:
        print("No keywords in database.")
        return

    key_id, keyword = result

    # 2. Fetch all emojis (converted to hex) associated with this keyword
    cursor.execute("""
        SELECT c.`char`
        FROM chardef c
        JOIN entry e ON c.rowid = e.chardef_id
        WHERE e.keydef_id = ?
    """, (key_id,))

    rows = [row[0] for row in cursor.fetchall()]

    print(f"Keyword: '{keyword}'")
    # print(f"Associated Emojis (hex): {', '.join(hex_codes) if hex_code else 'None found'}")
    for hex_code in rows:
        print(f"Associated Emojis ({emojilized(hex_code)}): {hex_code if hex_code else 'None found'}")

    print("\n")

def test(dbPath):
    if not os.path.isfile(dbPath):
        sys.exit("Error: Database file not found for test.")

    db = sqlite3.connect(dbPath)
    cursor = db.cursor()

    print("\n\n")
    test_fetch_random_emoji_with_keywords(cursor)
    test_fetch_random_keyword_with_emojis(cursor)

    db.close()

def main():
    arg_reader = argparse.ArgumentParser(description='emoji.db Utility')
    arg_reader.add_argument('--update', action=argparse.BooleanOptionalAction, help='Update CLDR and Unicode emoji json/txt files (into --dir)')
    arg_reader.add_argument('--run', action=argparse.BooleanOptionalAction, help='Run import (into --output DB file) and generate Swift JSON')
    arg_reader.add_argument('--test', action=argparse.BooleanOptionalAction, help='Run test')
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
        apply_ranking()

        sys.exit(0)

    if args.test:
        if not args.output:
            print("Error: Output database file path (-o/--output) is required for --run.")
            sys.exit(1)
        # test(args.test, args.output)
        test(args.output)


    if not any(vars(args).values()):
        arg_reader.print_help()
        sys.exit(0)

if __name__ == "__main__":
    main()