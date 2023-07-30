#!/usr/bin/env python
#
# version: 0.1.0
# autor: Ethan Liu
#
# convert cin table to sqlite db

import argparse
import importlib
import sys, os
# import re
# import json
import sqlite3
from enum import IntEnum
from tqdm import tqdm
from lib.cintable import CinTable
# from time import sleep

uu = importlib.import_module("lib.util")

# CIN_TAG = [
#     '%gen_inp',
#     '%encoding',
#     '%name',
#     '%endkey',
#     '%selkey',

#     '%cname',
#     '%ename',
#     '%tcname',
#     '%scname',
#     '%locale',
# ]

# CIN_SECTION = [
#     '%keyname',
#     '%chardef',
# ]

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

class Mode(IntEnum):
    CREATE = 1
    APPEND = 2

    def __repr__(self):
        return self.name[0]

    def __str__(self):
        return self.name[0]

def performImport(cursor, inputPath, mode = Mode.CREATE):
    # tqdm.write(uu.color(f"[{filename}]", fg = 'green'))
    cin = CinTable(inputPath, level = 3)

    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA journal_mode = MEMORY")
    cursor.execute("BEGIN TRANSACTION")

    if mode == Mode.CREATE:
        query = "INSERT OR IGNORE INTO `info` (`name`, `value`) VALUES (:name, :value)"
        for key in cin.info:
            value = cin.info[key]
            if value:
                args = {'name': key, 'value': value}
                cursor.execute(query, args)

        filename = os.path.basename(inputPath)
        if filename in HANS_TABLE:
            args = {'name': 'locale', 'value': 'zh-Hans'}
            cursor.execute(query, args)

        query = "INSERT OR IGNORE INTO `keyname` (`key`, `value`) VALUES (:name, :value)"
        for key in cin.keyname:
            args = {'name': key, 'value': cin.keyname[key]}
            cursor.execute(query, args)

    query1 = "INSERT OR IGNORE INTO `keydef` (`key`) VALUES (:value)"
    query2 = "SELECT `rowid` FROM `keydef` WHERE `key` = :value LIMIT 1"
    query3 = "INSERT OR IGNORE INTO `chardef` (`char`) VALUES (:value)"
    query4 = "SELECT `rowid` FROM `chardef` WHERE `char` = :value LIMIT 1"
    query5 = "INSERT OR IGNORE INTO `entry` (`keydef_id`, `chardef_id`) VALUES (:kid, :cid)"

    for item in tqdm(cin.chardef, unit = 'MB', unit_scale = True, ascii = True, desc = f"{cin.getName()}"):
        # print(f"{item[0]} => {item[1]}")
        key = item[0]
        value = item[1]

        # keydef
        args = {'value': key}
        cursor.execute(query1, args)
        keydefId = uu.getOne(cursor, query2, args)

        # chardef
        args = {'value': value}
        cursor.execute(query3, args)
        chardefId = uu.getOne(cursor, query4, args)

        #entry pivot
        args = {'kid': keydefId, 'cid': chardefId}
        cursor.execute(query5, args)

    cursor.execute("COMMIT TRANSACTION")
    cursor.execute('VACUUM')


# def performImport_v1(cursor, inputPath, mode = Mode.CREATE):
#     section = None
#     skipSection = None

#     filename = os.path.basename(inputPath)
#     reader = open(inputPath, 'r')

#     cursor.execute("PRAGMA synchronous = OFF")
#     cursor.execute("PRAGMA journal_mode = MEMORY")
#     cursor.execute("BEGIN TRANSACTION")

#     tqdm.write(uu.color(f"[{filename}]", fg = 'green'))

#     for row in tqdm(reader.readlines(), unit = 'MB', unit_scale = True, ascii = True, desc = f"[{mode}] {filename}"):
#     # for row in reader.readlines():
#         # pbar.set_description(f"{filename} {row}")
#         row = uu.trim(row, '#')
#         if not row or row == '':
#             continue

#         items = re.split('[\s\t]{1}', row, 1)
#         if len(items) < 2:
#             continue

#         key = uu.trim(items[0]).lower()
#         value = uu.trim(items[1])

#         if key in CIN_SECTION:
#             if section == key and value == 'end':
#                 # tqdm.write(f"End of Section: {section}")
#                 section = None
#                 skipSection = None
#             else:
#                 # section = key[1:]
#                 section = key
#                 skipSection = None
#                 # tqdm.write(f"Begin: {section}")
#                 if key == '%chardef' and mode == Mode.CREATE:
#                     # patch name
#                     # patch locale
#                     if filename in HANS_TABLE:
#                         query = "INSERT INTO `info` (`name`, `value`) VALUES (:name, :value)"
#                         args = {'name': 'locale', 'value': 'zh-Hans'}
#                         tqdm.write(f"[info] {args['name']} = {args['value']}")
#                         cursor.execute(query, args)
#             continue

#         if not section:

#             if skipSection:
#                 # tqdm.write(f"[?] skip section: {key} / {skipSection}")
#                 continue

#             if key.startswith('%') and (value == 'begin' or value == 'end'):
#                 skipSection = key
#                 tqdm.write(f"[?] Unknown section: {key}")
#                 continue

#             if not key in CIN_TAG:
#                 tqdm.write(f"[?] Unknown tag: {key}")
#                 continue

#             if mode == Mode.CREATE:
#                 tqdm.write(f"[i] {key[1:]} = {value}")
#                 query = "INSERT OR IGNORE INTO `info` (`name`, `value`) VALUES (:name, :value)"
#                 args = {'name': key[1:], 'value': value}
#                 cursor.execute(query, args)

#             continue


#         if section == '%keyname':
#             query = "INSERT OR IGNORE INTO `keyname` (`key`, `value`) VALUES (:key, :value)"
#             args = {'key': key, 'value': value}
#             cursor.execute(query, args)
#             continue

#         if section == '%chardef':
#             # keydef
#             query = "INSERT OR IGNORE INTO `keydef` (`key`) VALUES (:value)"
#             args = {'value': key}
#             cursor.execute(query, args)
#             query = "SELECT `rowid` FROM `keydef` WHERE `key` = :value LIMIT 1"
#             keydefId = uu.getOne(cursor, query, args)

#             # chardef
#             query = "INSERT OR IGNORE INTO `chardef` (`char`) VALUES (:value)"
#             args = {'value': value}
#             cursor.execute(query, args)
#             query = "SELECT `rowid` FROM `chardef` WHERE `char` = :value LIMIT 1"
#             chardefId = uu.getOne(cursor, query, args)

#             #entry pivot
#             query = "INSERT OR IGNORE INTO `entry` (`keydef_id`, `chardef_id`) VALUES (:kid, :cid)"
#             args = {'kid': keydefId, 'cid': chardefId}
#             cursor.execute(query, args)

#     reader.close()
#     cursor.execute("COMMIT TRANSACTION")
#     cursor.execute('VACUUM')

# def performArray30(category, cursor, path):
#     if not (category == 'shortcode' or category == 'special'):
#         print("Invalid category")
#         return

#     keydefTableName = f"keydef_{category}"
#     entryTableName = f"entry_{category}"
#     entryKeydefColumnName = f"keydef_{category}_id"

#     # cursor.execute(f"CREATE TABLE {keydefTableName} (`key` CHAR(255) UNIQUE NOT NULL)")
#     # cursor.execute(f"CREATE TABLE {entryTableName} (`{entryKeydefColumnName}` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL)")

#     begin = False

#     filename = os.path.basename(path)
#     reader = open(path, 'r')

#     cursor.execute("PRAGMA synchronous = OFF")
#     cursor.execute("PRAGMA journal_mode = MEMORY")
#     cursor.execute("BEGIN TRANSACTION")

#     for row in tqdm(reader.readlines(), unit = 'MB', unit_scale = True, ascii = True, desc = f"[{filename}"):
#         row = uu.trim(row, '#')
#         if not row or row == '':
#             continue

#         if row == '%chardef begin':
#             begin = True
#             continue

#         if row == '%chardef end':
#             begin = False
#             continue

#         if not begin:
#             continue

#         items = re.split('[\s\t]{1}', row, 1)
#         if len(items) < 2:
#             continue

#         key = uu.trim(items[0])
#         value = uu.trim(items[1])

#         # keydef
#         query = f"INSERT OR IGNORE INTO `{keydefTableName}` (`key`) VALUES (:value)"
#         args = {'value': key}
#         cursor.execute(query, args)
#         query = f"SELECT `rowid` FROM `{keydefTableName}` WHERE `key` = :value LIMIT 1"
#         keydefId = uu.getOne(cursor, query, args)

#         # chardef
#         query = "INSERT OR IGNORE INTO `chardef` (`char`) VALUES (:value)"
#         args = {'value': value}
#         cursor.execute(query, args)
#         query = "SELECT `rowid` FROM `chardef` WHERE `char` = :value LIMIT 1"
#         chardefId = uu.getOne(cursor, query, args)

#         # entry pivot
#         query = f"INSERT OR IGNORE INTO `{entryTableName}` (`{entryKeydefColumnName}`, `chardef_id`) VALUES (:kid, :vid)"
#         args = {'kid': keydefId, 'vid': chardefId}
#         cursor.execute(query, args)

#     reader.close()
#     cursor.execute("COMMIT TRANSACTION")
#     cursor.execute('VACUUM')

def validate(cursor):
    cursor.execute("SELECT key, value FROM `keyname` ORDER BY rowid")
    result = cursor.fetchall()
    for item in tqdm(result, unit_scale = True, ascii = True, desc = f"Validation"):
        query = "SELECT COUNT(rowid) FROM `keydef` WHERE key LIKE :key"
        check = uu.getOne(cursor, query, {'key': f"%{item[0]}%"})
        if not check or check <= 1:
            tqdm.write(f"[?] keyname: {item[0]} ({item[1]}) never or rarely used")

def pluginArray(cursor, inputs):
    basedir = os.path.dirname(inputs[0])
    for category in ['shortcode', 'special']:
        path = f"{basedir}/array-{category}.cin"
        if not os.path.exists(path):
            tqdm.write(f"File not found: {path}")
            continue

        cin = CinTable(path, level = 3)

        keydefTableName = f"keydef_{category}"
        entryTableName = f"entry_{category}"
        entryKeydefColumnName = f"keydef_{category}_id"

        cursor.execute(f"CREATE TABLE {keydefTableName} (`key` CHAR(255) UNIQUE NOT NULL)")
        cursor.execute(f"CREATE TABLE {entryTableName} (`{entryKeydefColumnName}` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL)")

        query1 = f"INSERT OR IGNORE INTO `{keydefTableName}` (`key`) VALUES (:value)"
        query2 = f"SELECT `rowid` FROM `{keydefTableName}` WHERE `key` = :value LIMIT 1"
        query3 = "INSERT OR IGNORE INTO `chardef` (`char`) VALUES (:value)"
        query4 = "SELECT `rowid` FROM `chardef` WHERE `char` = :value LIMIT 1"
        query5 = f"INSERT OR IGNORE INTO `{entryTableName}` (`{entryKeydefColumnName}`, `chardef_id`) VALUES (:kid, :vid)"

        cursor.execute("BEGIN TRANSACTION")
        for item in tqdm(cin.chardef, unit = 'MB', unit_scale = True, ascii = True, desc = f"{cin.getName()}"):
            # tqdm.write(f"{item[0]} => {item[1]}")
            key = item[0]
            value = item[1]

            # keydef
            args = {'value': key}
            cursor.execute(query1, args)
            keydefId = uu.getOne(cursor, query2, args)

            # chardef
            args = {'value': value}
            cursor.execute(query3, args)
            chardefId = uu.getOne(cursor, query4, args)

            # entry pivot
            args = {'kid': keydefId, 'vid': chardefId}
            cursor.execute(query5, args)

        cursor.execute("COMMIT TRANSACTION")
    cursor.execute('VACUUM')

def pluginBossy(cursor):
    query = "UPDATE `info` SET value = :value WHERE `name` = :name"
    args = {'name': 'ename', 'value': "Bossy"}
    cursor.execute(query, args)
    args = {'name': 'cname', 'value': "謥蝦米"}
    cursor.execute(query, args)
    pass

def main():
    argParser = argparse.ArgumentParser(description='Convert cin table to sqlite db file')
    argParser.add_argument('-i', '--input', type = str, required = True, nargs = '+', help='The cin table file(s), the first one would be the major table for information')
    argParser.add_argument('-o', '--output', type = str, required = True, help='The sqlite file path')
    # argParser.add_argument('-t', '--test', type = str, help='The database file path')
    # argParser.add_argument('--header', type = str, help='The custom CIN table header file path')
    # argParser.add_argument('--array-shortcode', type = str, help='The input file path of array-shortcode.cin')
    # argParser.add_argument('--array-special', type = str, help='The input file path of array-special.cin')
    argParser.add_argument('-e', '--plugin', choices=['array', 'bossy'], help='plugin')

    args = argParser.parse_args()
    # print(args, len(sys.argv))
    # sys.exit(0)

    for path in args.input:
        if not os.path.exists(path):
            print(f"File not found: {path}")
            sys.exit(0)

    if os.path.exists(args.output):
        # print(f"Remove existing file: {args.output}")
        os.remove(args.output)

    db = sqlite3.connect(args.output)
    cursor = db.cursor()

    # main table
    cursor.execute("CREATE TABLE info (`name` CHAR(255) UNIQUE NOT NULL, `value` CHAR(255) default '')")
    cursor.execute("CREATE TABLE keyname (`key` CHAR(255) UNIQUE NOT NULL, `value` CHAR(255) default '')")
    cursor.execute("CREATE TABLE keydef (`key` CHAR(255) UNIQUE NOT NULL)")
    cursor.execute("CREATE TABLE chardef (`char` CHAR(255) UNIQUE NOT NULL)")
    cursor.execute("CREATE TABLE entry (`keydef_id` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL, UNIQUE(`keydef_id`, `chardef_id`) ON CONFLICT IGNORE)")
    # # shortcode table
    # cursor.execute(f"CREATE TABLE keydef_shortcode (`key` CHAR(255) UNIQUE NOT NULL)")
    # cursor.execute(f"CREATE TABLE entry_shortcode (`keydef_shortcode_id` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL)")
    # # special table
    # cursor.execute(f"CREATE TABLE keydef_special (`key` CHAR(255) UNIQUE NOT NULL)")
    # cursor.execute(f"CREATE TABLE entry_special (`keydef_special_id` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL)")

    mode = Mode.CREATE
    for index, path in enumerate(args.input):
        if index > 0:
            mode = Mode.APPEND
        # print(f"{index}: {mode} {path}")
        performImport(cursor, path, mode)
        db.commit()

    if args.plugin:
        match args.plugin:
            case "array":
                pluginArray(cursor, args.input)
            case "bossy":
                pluginBossy(cursor)
        db.commit()

    # if args.array_shortcode and os.path.exists(args.array_shortcode):
    #     performArray30('shortcode', cursor, args.array_shortcode)
    #     db.commit()

    # if args.array_special and os.path.exists(args.array_special):
    #     performArray30('special', cursor, args.array_special)
    #     db.commit()

    validate(cursor)
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
