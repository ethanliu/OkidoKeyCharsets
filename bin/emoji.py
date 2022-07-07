#!/usr/bin/env python
#
# version: 0.0.1
# autor: Ethan Liu
#
# all about emoji
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

COMMON_WORDS_LIST = ['skin tone', '皮膚', '肤色']

def updateResources():
    package = "cldr-annotations-derived-full"
    langs = ['en', 'zh-Hant', 'zh']

    pool = urllib3.PoolManager()

    for lang in langs:
        url = 'https://github.com/unicode-org/cldr-json/raw/main/cldr-json/{}/annotationsDerived/{}/annotations.json'.format(package, lang)
        path = 'tmp/emoji-cldr-{}.json'.format(lang)

        # req = requests.get(url, verify=False)
        # open(path, 'w').write(req.text)

        print('download: ' + path)
        with pool.request('GET', url, preload_content=False) as res, open(path, 'wb') as f:
            shutil.copyfileobj(res, f)

        res.release_conn()
        # print('download: ' + url + '\n' + path)

    sys.exit(0)

def parse(lang, cursor):
    path = "tmp/emoji-cldr-{}.json".format(lang)
    file = open(path, 'r')
    data = json.load(file)
    file.close()

    # version = data['annotationsDerived']['identity']['version']['_cldrVersion']
    # cursor.execute("INSERT INTO info VALUES (?, ?)", ("version", version))
    # cursor.execute("BEGIN TRANSACTION")

    count = 0

    for emoji in data['annotationsDerived']['annotations']:
        codes = emoji.encode('unicode-escape').decode('ascii')
        # codes = list(filter(None, codes.split('\\U')))
        codes = list(filter(None, re.split(r'\\U', codes, flags=re.IGNORECASE)))
        codes = ' '.join(codes).upper()
        # print(codes)

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
        if not 'default' in data['annotationsDerived']['annotations'][emoji]:
            # print("emoji: {} has no keywords".format(emoji))
            continue

        keywords = data['annotationsDerived']['annotations'][emoji]['default']
        # print(emoji, data['annotationsDerived']['annotations'][emoji])

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
                count += 1

            # entry pivot
            if keydefId > 0 and chardefId > 0:
                # print('k:{}, v:{}'.format(keydefId, chardefId))
                cursor.execute("INSERT INTO entry VALUES (?, ?)", (keydefId, chardefId))


        # count += 1
        # if count > 10:
        #     break

    # cursor.execute("COMMIT TRANSACTION")
    print("{}: {} keywords".format(lang, count))


def main():
    argParser = argparse.ArgumentParser(description='emoji utility')
    # argParser.add_argument('output', default='tmp/emoji.db', help='output file path')
    argParser.add_argument('--update', action=argparse.BooleanOptionalAction, help='Update emoji cldr json files')

    args = argParser.parse_args()
    # print(args)

    if args.update:
        updateResources()


    dbPath = 'tmp/emoji.db'

    if os.path.isfile(dbPath):
        os.remove(dbPath)

    db = sqlite3.connect(dbPath)
    cursor = db.cursor()

    cursor.execute("CREATE TABLE info (`name` CHAR(255) UNIQUE NOT NULL, `value` CHAR(255) default '')")
    # cursor.execute("CREATE TABLE keyname (`key` CHAR(255) UNIQUE NOT NULL, `value` CHAR(255) default '')")
    cursor.execute("CREATE TABLE keydef (`key` CHAR(255) UNIQUE NOT NULL)")
    cursor.execute("CREATE TABLE chardef (`char` CHAR(255) UNIQUE NOT NULL)")
    cursor.execute("CREATE TABLE entry (`keydef_id` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL)")

    parse('zh-Hant', cursor)
    parse('en', cursor)
    parse('zh', cursor)

    db.commit()
    db.close()
    print("emoji db: " + dbPath)

    sys.exit(0)

if __name__ == "__main__":
    main()
