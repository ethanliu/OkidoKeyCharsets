#!/usr/bin/env python
#
# version: 0.0.5
# autor: Ethan Liu
#
# all about emoji
# since all we need for emoji are only a few files
# using the whole repo is kinda heavy, download individual file instead
#
# refs:
# https://github.com/unicode-org/cldr-json

import argparse
import sys, os
import urllib3
import shutil
import re
import json
import sqlite3

# import requests
# import ssl
# import certifi
# import codecs

# REPO_PATH = os.path.realpath(os.path.dirname(__file__) + '/../rawdata/cldr-json/cldr-json')

COMMON_WORDS_LIST = ['skin tone', '皮膚', '肤色']

PACKAGES_LIST = [
    'cldr-annotations-derived-full/annotationsDerived/{}/annotations.json',
    'cldr-annotations-full/annotations/{}/annotations.json',
]

LANGS = ['en', 'zh-Hant', 'zh']

def updateResources(basedir):
    baseurl = 'https://github.com/unicode-org/cldr-json/raw/main/cldr-json'
    pool = urllib3.PoolManager()

    for package in PACKAGES_LIST:
        for lang in LANGS:
            url = f"{baseurl}/{package.format(lang)}"
            path = f"{basedir}/{package.format(lang).replace('/', '_')}"

            print(f"Download: {path}")
            with pool.request('GET', url, preload_content=False) as res, open(path, 'wb') as f:
                shutil.copyfileobj(res, f)

            res.release_conn()
    print("Update finished")

def charToLongHex(emoji):
    codes = emoji.encode('unicode-escape').decode('ascii')
    codes = list(filter(None, re.split(r'\\U|\\x', codes, flags=re.IGNORECASE)))
    # print(emoji, codes, path),

    for index, code in enumerate(codes):
        try:
            v = int(code, 16)
        except ValueError:
            # print("Ignore annotation: ", emoji, codes)
            # continue
            # break
            return None

        v = f"{v:08x}"
        codes[index] = v

    codes = ' '.join(codes).upper()
    return codes


def parse(cursor, path):
    file = open(path, 'r')
    data = json.load(file)
    file.close()

    # version = data['annotationsDerived']['identity']['version']['_cldrVersion']
    # cursor.execute("INSERT INTO info VALUES (?, ?)", ("version", version))
    # cursor.execute("BEGIN TRANSACTION")

    node = None
    # count = 0

    if 'annotationsDerived' in data:
        node = data['annotationsDerived']['annotations']
    elif 'annotations' in data:
        node = data['annotations']['annotations']
    else:
        print("node not found: " + path)
        return

    for emoji in node:
        codes = charToLongHex(emoji)
        if codes == None:
            print(f"Skip: {emoji}")
            continue;

        # chardef
        cursor.execute("SELECT rowid FROM chardef WHERE char = ? LIMIT 1", (codes,))
        # chardefId = cursor.fetchone()
        result = cursor.fetchone()

        if result:
            chardefId = result[0]
        else:
            cursor.execute("INSERT INTO chardef VALUES (?)", (codes,))
            chardefId = cursor.lastrowid

        # print('#{} -> {}'.format(chardefId, codes))

        # an quick but unsafe check but since prefix is all we need here
        if not 'default' in node[emoji]:
            # print("emoji: {} has no keywords".format(emoji))
            continue

        keywords = node[emoji]['default']
        # print(emoji, node[emoji])

        # print(keywords)
        for keyword in keywords:
            # if 'skin tone' in keyword:
            if any(words in keyword for words in COMMON_WORDS_LIST):
                continue
            # print(keyword)
            # keydef
            cursor.execute("SELECT rowid FROM keydef WHERE key = :value LIMIT 1", {'value': keyword})
            result = cursor.fetchone()

            if result:
                keydefId = result[0]
            else:
                cursor.execute("INSERT INTO keydef VALUES (:value)", {'value': keyword})
                keydefId = cursor.lastrowid

            # entry pivot
            if keydefId > 0 and chardefId > 0:
                # print('k:{}, v:{}'.format(keydefId, chardefId))
                cursor.execute("INSERT INTO entry VALUES (?, ?)", (keydefId, chardefId))


        # count += 1
        # if count > 10:
        #     break

    # cursor.execute("COMMIT TRANSACTION")
    # print("{}: {} keywords".format(lang, count))

def performImport(repoPath, dbPath):
    if os.path.isfile(dbPath):
        os.remove(dbPath)

    db = sqlite3.connect(dbPath)
    cursor = db.cursor()

    cursor.execute("CREATE TABLE info (`name` CHAR(255) NOT NULL, `value` CHAR(255) default '')")
    cursor.execute("CREATE TABLE keydef (`key` CHAR(255) NOT NULL)")
    cursor.execute("CREATE TABLE chardef (`char` CHAR(255) NOT NULL)")
    cursor.execute("CREATE TABLE entry (`keydef_id` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL)")

    for package in PACKAGES_LIST:
        for lang in LANGS:
            # path = f"{args.repo}/{package}".format(lang)
            path = f"{repoPath}/{package.format(lang).replace('/', '_')}"
            # print(path)
            if not os.path.isfile(path):
                print(f"Path not found: {path}")
                continue
            parse(cursor, path)

    db.commit()

    # index
    cursor.execute('vacuum')
    cursor.execute("CREATE UNIQUE INDEX info_index ON info (name)")
    cursor.execute("CREATE UNIQUE INDEX keydef_index ON keydef (key)")
    cursor.execute("CREATE UNIQUE INDEX chardef_index ON chardef (char)")
    cursor.execute("CREATE INDEX entry_index ON entry (keydef_id, chardef_id)")

    cursor.execute("SELECT COUNT(*) FROM chardef")
    characterCounter = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM keydef")
    keywordsCounter = cursor.fetchone()[0]

    db.close()

    print(f"\nOutput: {dbPath}")
    print(f"Counter: chardef: {characterCounter}, keydef: {keywordsCounter}")

def emojilized(hexString):
    codes = r'\U' + r'\U'.join(hexString.split(' '))
    codes = codes.encode('utf8').decode('unicode-escape')
    return codes

def test(phrase, dbPath):
    if not os.path.isfile(dbPath):
        sys.exit("File not found")

    db = sqlite3.connect(dbPath)
    cursor = db.cursor()
    prefix = "EXPLAIN QUERY PLAN "

    if phrase == 'emoji':
        cursor.execute(prefix + "SELECT * FROM chardef WHERE rowid In (SELECT rowid FROM chardef ORDER BY RANDOM() LIMIT 100)")
        result = cursor.fetchall()

        if not result:
            return

        for item in result:
            emoji = emojilized(item[0])
            print(emoji, end = ' '),
        print('')

    else:
        # cursor.execute("SELECT * FROM keydef WHERE rowid IN (SELECT rowid FROM keydef ORDER BY RANDOM() LIMIT 10)")
        # cursor.execute("SELECT * FROM keydef WHERE key LIKE :phrase", {'phrase': '%' + phrase + '%'})
        cursor.execute(prefix + "SELECT DISTINCT chardef.char, keydef.key FROM keydef, chardef, entry WHERE 1 AND  (keydef.key LIKE ? OR keydef.key LIKE ? OR keydef.key LIKE ? OR keydef.key LIKE ?) AND keydef.ROWID = entry.keydef_id AND chardef.ROWID = entry.chardef_id ", [phrase, f'% {phrase} %', f'%{phrase} %', f'% {phrase}%'])

        result = cursor.fetchall()

        if not result:
            print("No result for phrase: ", phrase)
            return

        if prefix:
            print(result)
        else:
            for item in result:
                print(emojilized(item[0]), item[1])

    db.close()
    # print("\nEnd of test")


def main():
    argParser = argparse.ArgumentParser(description='emoji.db Utility')
    argParser.add_argument('--update', action=argparse.BooleanOptionalAction, help='Update emoji cldr json files')
    argParser.add_argument('--run', action=argparse.BooleanOptionalAction, help='Run import')
    argParser.add_argument('-test', type = str, help='Test keyword')
    argParser.add_argument('-d', '--dir', type = str, help='The directory path of cldr-json files')
    argParser.add_argument('-o', '--output', type = str, help='The file path of emoji.db')

    args = argParser.parse_args()
    # print(args, len(sys.argv))
    # sys.exit(0)

    # if len(sys.argv) < 2:
    #     argParser.print_usage()
    #     sys.exit(0)

    if args.update:
        if not args.dir or not os.path.exists(args.dir):
            print(f"Directory (rawdata/emoji) not found: {args.dir}")
            sys.exit(0)
        updateResources(args.dir)
        sys.exit(0)

    if args.test:
        if not args.output or not os.path.isfile(args.output):
            print(f"File (emoji.db) not found or missing: {args.output}")
            sys.exit(0)
        test(args.test, args.output)
        sys.exit(0)

    if args.run:
        if not args.dir or not os.path.exists(args.dir):
            print(f"Directory (rawdata/emoji) not found: {args.dir}")
            sys.exit(0)
        performImport(args.dir, args.output);

    sys.exit(0)

if __name__ == "__main__":
    main()
