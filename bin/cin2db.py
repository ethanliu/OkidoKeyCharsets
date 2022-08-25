#!/usr/bin/env python
#
# version: 0.0.2
# autor: Ethan Liu
#
# convert cin table to sqlite db

import argparse
import importlib
import sys, os
import re
# import json
import sqlite3
from tqdm import tqdm
# from time import sleep

uu = importlib.import_module("lib.util")

CIN_TAG = [
    '%gen_inp',
    # '%encoding',
    '%name',
    '%endkey',
    '%selkey',

    '%cname',
    '%ename',
    '%tcname',
    '%scname',
    '%locale',
]

CIN_SECTION = [
    '%keyname',
    '%chardef',
]

HANS_TABLE = [
    "ghcm.cin",
    "jidianwubi.cin",
    "jtcj.cin",
    "lxsy.cin",
    "lxsy_0.40.cin",
    "lxsy_0.41.cin",
    "pinyin.cin",
    "shuangpin.cin",
    "wubizixing.cin",
    "wus.cin",
]

# TODO: suggest keyboard layout?

debugLevel = 0


def performImport(cursor, inputPath, partial = False):
    section = None

    # print(f"Import file: {os.path.basename(inputPath)}")
    filename = os.path.basename(inputPath)
    reader = open(inputPath, 'r')

    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA journal_mode = MEMORY")
    cursor.execute("BEGIN TRANSACTION")

    for row in tqdm(reader.readlines(), unit = 'MB', unit_scale = True, ascii = True, desc = filename):
    # for row in reader.readlines():
        # pbar.set_description(f"{filename} {row}")
        row = uu.trim(row, '#')
        if not row or row == '':
            continue

        items = re.split('[\s|\t]{1}', row, 1)
        if len(items) < 2:
            continue

        key = uu.trim(items[0])
        value = uu.trim(items[1])

        if key in CIN_SECTION:
            if section == key and value == 'end':
                # tqdm.write(f"End of Section: {section}")
                section = None
            else:
                # section = key[1:]
                section = key
                # tqdm.write(f"Begin: {section}")
                if key == '%chardef' and not partial:
                    # patch name
                    # patch locale
                    if filename in HANS_TABLE:
                        query = "INSERT INTO info (`name`, `value`) VALUES (:name, :value)"
                        args = {'name': 'locale', 'value': 'zh-Hans'}
                        tqdm.write(f"[info] {args['name']} = {args['value']}")
                        cursor.execute(query, args)
            continue

        if not section:
            if not key in CIN_TAG:
                tqdm.write(f"Invalid tag: {key}")
                continue

            if not partial:
                tqdm.write(f"[info] {key[1:]} = {value}")
                query = "SELECT rowid FROM info WHERE `name` = :name"
                args = {'name': key[1:]}
                result = uu.getOne(cursor, query, args)

                if not result:
                    query = "INSERT INTO info (`name`, `value`) VALUES (:name, :value)"
                    args = {'name': key[1:], 'value': value}
                    cursor.execute(query, args)

            continue

        if not partial and section == '%keyname':
            query = "SELECT rowid FROM keyname WHERE `key` = :key"
            args = {'key': key}
            result = uu.getOne(cursor, query, args)
            if result:
                tqdm.write(f"[warn] duplicate keyname: {key}")
            else:
                query = "INSERT INTO keyname (`key`, `value`) VALUES (:key, :value)"
                args = {'key': key, 'value': value}
                cursor.execute(query, args)

        if section == '%chardef':
            query = "SELECT rowid FROM keydef WHERE `key` = :key"
            args = {'key': key}
            result = uu.getOne(cursor, query, args)
            if result:
                keydefId = result
            else:
                query = "INSERT INTO keydef (`key`) VALUES (:value)"
                args = {'value': key}
                cursor.execute(query, args)
                keydefId = cursor.lastrowid

            query = "SELECT rowid FROM chardef WHERE `char` = :char"
            args = {'char': value}
            result = uu.getOne(cursor, query, args)

            if result:
                chardefId = result
            else:
                query = "INSERT INTO chardef (`char`) VALUES (:value)"
                args = {'value': value}
                cursor.execute(query, args)
                chardefId = cursor.lastrowid

            query = "INSERT INTO entry (`keydef_id`, `chardef_id`) VALUES (:kid, :vid)"
            args = {'kid': keydefId, 'vid': chardefId}
            cursor.execute(query, args)

    reader.close()
    cursor.execute("COMMIT TRANSACTION")
    cursor.execute('VACUUM')


    # counters = []

    # counters.append(uu.getOne(cursor, "SELECT COUNT(*) FROM chardef"))
    # print(counters)

    # cursor.execute("SELECT COUNT(*) FROM keydef")
    # keywordsCounter = cursor.fetchone()[0]

# def performTest(path):
#     total = 1000
#     db = sqlite3.connect(path)
#     cursor = db.cursor()
#     cursor.execute("SELECT `key` FROM `keydef` ORDER BY RANDOM() LIMIT :total", {'total': total})
#     keys = cursor.fetchall()
#     for key in keys:
#         query = "SELECT DISTINCT chardef.char AS char FROM chardef, keydef, entry WHERE keydef.key = :value AND keydef.rowid = entry.keydef_id AND chardef.rowid = entry.chardef_id ORDER BY keydef.rowid"
#         cursor.execute(query, {'value': key[0]})
#         result = cursor.fetchall()
#         print(f"\n{key[0]} => ", end = '')
#         for item in result:
#             print(item[0], end = '')
#         # cursor.execute("SELECT DISTINCT chardef.char, keydef.key FROM keydef, chardef, entry WHERE 1 AND  (keydef.key LIKE ? OR keydef.key LIKE ? OR keydef.key LIKE ? OR keydef.key LIKE ?) AND keydef.ROWID = entry.keydef_id AND chardef.ROWID = entry.chardef_id ", [phrase, f'% {phrase} %', f'%{phrase} %', f'% {phrase}%'])


def main():
    argParser = argparse.ArgumentParser(description='Convert cin table to sqlite db file')
    argParser.add_argument('-i', '--input', type = str, required = True, help='The cin table file path')
    argParser.add_argument('-o', '--output', type = str, required = True, help='The sqlite file path')
    # argParser.add_argument('-t', '--test', type = str, help='The database file path')
    # argParser.add_argument('-i', '--input', type = str, help='The input file path of cin table file')
    # argParser.add_argument('-o', '--output', type = str, help='The output file path')
    # argParser.add_argument('--header', type = str, help='The custom CIN table header file path')
    argParser.add_argument('--array-short', type = str, help='The input file path of array-shortcode.cin')
    argParser.add_argument('--array-special', type = str, help='The input file path of array-special.cin')

    args = argParser.parse_args()
    # print(args, len(sys.argv))
    # sys.exit(0)

    # if args.test:
    #     if not os.path.exists(args.test):
    #         print(f"File not found: {args.input}")
    #         sys.exit(0)
    #     performTest(args.test)
    #     sys.exit(0)

    if not args.input or not os.path.exists(args.input):
        print(f"Input file missing or not found: {args.input}")
        sys.exit(0)

    if not args.output:
        print(f"Output file path missing")
        sys.exit(0)

    if os.path.exists(args.output):
        # print(f"Remove existing file: {args.output}")
        os.remove(args.output)


    db = sqlite3.connect(args.output)
    cursor = db.cursor()

    cursor.execute("CREATE TABLE info (`name` CHAR(255) UNIQUE NOT NULL, `value` CHAR(255) default '')")
    cursor.execute("CREATE TABLE keyname (`key` CHAR(255) UNIQUE NOT NULL, `value` CHAR(255) default '')")
    cursor.execute("CREATE TABLE keydef (`key` CHAR(255) UNIQUE NOT NULL)")
    cursor.execute("CREATE TABLE chardef (`char` CHAR(255) UNIQUE NOT NULL)")
    cursor.execute("CREATE TABLE entry (`keydef_id` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL)")

    # cursor.execute("CREATE UNIQUE INDEX keydef_index ON keydef (key)")
    # cursor.execute("CREATE UNIQUE INDEX chardef_index ON chardef (char)")

    performImport(cursor, args.input)
    db.commit()

    if args.array_short and os.path.exists(args.array_short):
        cursor.execute("CREATE TABLE keydef_shortcode (`key` CHAR(255) UNIQUE NOT NULL)")
        cursor.execute("CREATE TABLE entry_shortcode (`keydef_shortcode_id` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL)")
        # cursor.execute("CREATE UNIQUE INDEX keydef_shortcode_index ON keydef (key)")
        performImport(cursor, args.array_short, True)
        db.commit()

    if args.array_special and os.path.exists(args.array_special):
        cursor.execute("CREATE TABLE keydef_special (`key` CHAR(255) UNIQUE NOT NULL)")
        cursor.execute("CREATE TABLE entry_special (`keydef_special_id` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL)")
        # cursor.execute("CREATE UNIQUE INDEX keydef_special_index ON keydef (key)")
        performImport(cursor, args.array_special, True)
        db.commit()

    db.close()

    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupt by user")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    # except BaseException as err:
