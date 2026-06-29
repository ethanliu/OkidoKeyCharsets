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

    found_tones = [SKIN_TONE_MAP[n] for n in nodes if n in SKIN_TONE_MAP]
    is_skin = 1 if found_tones else 0

    # A "Neutral" emoji has no skin tone but is the source for others
    is_neutral = 1 if not is_skin else 0
    is_zwj = 1 if ZWJ in nodes else 0
    has_vs = 1 if EMOJI_VS in nodes else 0

    tone1 = found_tones[0] if len(found_tones) > 0 else 0
    tone2 = found_tones[1] if len(found_tones) > 1 else 0

    # Strip skin tones and variation selectors to find the family ID
    parent_nodes = [n for n in nodes if n not in SKIN_TONE_MAP and n != EMOJI_VS]

    # Clean up ZWJ artifacts
    final_parent_nodes = []
    for node in parent_nodes:
        if node == ZWJ and (not final_parent_nodes or final_parent_nodes[-1] == ZWJ):
            continue
        final_parent_nodes.append(node)

    if final_parent_nodes and final_parent_nodes[-1] == ZWJ:
        final_parent_nodes.pop()

    parent_hex = ' '.join(final_parent_nodes)

    # If it's a simple emoji (like a heart or smile),
    # ensure parent_hex isn't empty
    if not parent_hex:
        parent_hex = hex_codes_string

    return is_skin, is_neutral, is_zwj, has_vs, tone1, tone2, parent_hex

def _collect_keywords(string_list, prefix):
    return [item.replace(prefix, '').strip() for item in string_list]

# Remove Variation Selectors (FE00 through FE0F)
def normalize_emoji_hex(char):
    clean_char = re.sub(r'[\ufe00-\ufe0f]', '', char)
    return ' '.join(f"{ord(c):08X}" for c in clean_char)
    # return ' '.join(f"{ord(c):08X}" for c in char)

def create_database():
    if os.path.isfile(DB_PATH): os.remove(DB_PATH)
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE chardef (
            `char` VARCHAR(255) UNIQUE NOT NULL,
            `is_base_template` INTEGER DEFAULT 0,
            `is_neutral` INTEGER DEFAULT 0,
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

    # remove_diacritics: strips accents and diacritics from characters during tokenization
    cursor.execute("""
        CREATE VIRTUAL TABLE emoji_search USING fts5(
            keywords,
            chardef_id UNINDEXED,
            tokenize="trigram remove_diacritics 1"
        );
    """)

    cursor.execute("CREATE INDEX idx_emoji_ranking ON chardef(is_base_template, is_skin_tone, weight)")
    cursor.execute("CREATE INDEX idx_emoji_lookup ON chardef(is_base_template, skin_tone_1, skin_tone_2, weight)")
    cursor.execute("CREATE INDEX idx_parent_lookup ON chardef(weight, parent_hex)")
    cursor.execute("CREATE INDEX idx_entry_lookup ON entry(keydef_id, chardef_id)")
    cursor.execute("CREATE INDEX idx_entry_reverse_lookup ON entry(chardef_id, keydef_id)")
    cursor.execute("CREATE INDEX idx_parent_hex ON chardef(parent_hex);")

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

            if not line or line.startswith("#"):
                continue

            # Sample: 1F44B 1F3FB ; fully-qualified # 👋🏻 E1.0 waving hand: light skin tone
            parts = line.split(";")
            if len(parts) < 2: continue

            hex_raw = parts[0].strip()
            status = parts[1].split("#")[0].strip()

            # We usually only want 'fully-qualified' for a clean database
            if status != "fully-qualified":
                continue

            h_code = pad_hex_to_8_digits(hex_raw)
            is_skin, is_neutral, is_zwj, has_vs, tone1, tone2, parent = analyze_emoji(h_code)

            cursor.execute("""
                INSERT OR IGNORE INTO chardef
                (char, is_skin_tone, is_neutral, is_zwj, has_vs, skin_tone_1, skin_tone_2, parent_hex)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (h_code, is_skin, is_neutral, is_zwj, has_vs, tone1, tone2, parent))

    cursor.execute("COMMIT TRANSACTION")

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

def populate_search_index():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM emoji_search;")

    cursor.execute("""
        INSERT INTO emoji_search (chardef_id, keywords)
        SELECT
            e.chardef_id,
            GROUP_CONCAT(k.key, ' ') || ' ' || GROUP_CONCAT(k.key, '') as keywords
        FROM entry e
        JOIN keydef k ON e.keydef_id = k.rowid
        GROUP BY e.chardef_id;
    """)

    cursor.execute("INSERT INTO emoji_search(emoji_search) VALUES('optimize')")

    conn.commit()
    cursor.execute("VACUUM")

    conn.close()

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


def test_emoji_keywords(cursor):
    print("--- Test: Random Emoji -> Keywords ---")

    # random chardef_id and its character string
    cursor.execute("SELECT rowid, `char` FROM chardef ORDER BY RANDOM() LIMIT 1")
    result = cursor.fetchone()

    if not result:
        print("Database is empty.")
        return

    char_id, hex_code = result
    emoji = emojilized(hex_code)

    # fetch all keys associated with this chardef
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

def test_keyword_emojis(cursor):
    print("--- Test: Random Keyword -> Emojis ---")

    # random keyword
    cursor.execute("SELECT rowid, `key` FROM keydef ORDER BY RANDOM() LIMIT 1")
    result = cursor.fetchone()

    if not result:
        print("No keywords in database.")
        return

    key_id, keyword = result

    # fetch all emojis associated with this keyword
    cursor.execute("""
        SELECT c.`char`
        FROM chardef c
        JOIN entry e ON c.rowid = e.chardef_id
        WHERE e.keydef_id = ?
    """, (key_id,))

    rows = [row[0] for row in cursor.fetchall()]

    print(f"Keyword: '{keyword}'")
    # print(f"Associated Emojis (hex): {', '.join(hex_codes) if hex_code else 'None found'}")
    print(f"Associated Emojis:")
    for hex_code in rows:
        print(f"{emojilized(hex_code)} => {hex_code if hex_code else 'None found'}")

    print("\n")

def test_skin_tone(cursor):
    query = """
        SELECT
            DISTINCT chardef.char
        FROM
            chardef, keydef, entry
        WHERE 1
            AND keydef.key LIKE "%醫%"
            AND keydef.rowid = entry.keydef_id
            AND chardef.rowid = entry.chardef_id
        GROUP BY chardef.char
        ORDER BY
            chardef.weight DESC
    """

    cursor.execute(query)
    rows = [row[0] for row in cursor.fetchall()]
    print("all emojis has keyword")
    for hex_code in rows:
        print(f"{emojilized(hex_code)} => {hex_code if hex_code else 'None found'}")


    query = """
        WITH RankedEmojis AS (
            SELECT
                c.char,
                c.weight,
                ROW_NUMBER() OVER (
                    PARTITION BY c.parent_hex
                    ORDER BY
                        (c.skin_tone_1 = 3) DESC,
                        c.is_skin_tone DESC,
                        c.weight DESC
                ) as rank
            FROM chardef c
            JOIN entry e ON c.rowid = e.chardef_id
            JOIN keydef k ON k.rowid = e.keydef_id
            WHERE k.key LIKE '%醫%'
        )
        SELECT char
        FROM RankedEmojis
        WHERE rank = 1
        ORDER BY weight DESC;
    """

    cursor.execute(query)
    rows = [row[0] for row in cursor.fetchall()]
    print("all emojis has keyword and prefferred skin tone")
    for hex_code in rows:
        print(f"{emojilized(hex_code)} => {hex_code if hex_code else 'None found'}")


def test(dbPath):
    if not os.path.isfile(dbPath):
        sys.exit("Error: Database file not found for test.")

    db = sqlite3.connect(dbPath)
    cursor = db.cursor()

    print("\n\n")
    test_emoji_keywords(cursor)
    test_keyword_emojis(cursor)
    test_skin_tone(cursor)

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
        populate_search_index()

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