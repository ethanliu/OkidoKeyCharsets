#!/usr/bin/env python
#
# autor: Ethan Liu
#
# convert cin table to sqlite db

import argparse
import importlib
import sys, os
import sqlite3
from enum import IntEnum
from tqdm import tqdm
from lib.cintable import CinTable, CinTableParseLevel
# from time import sleep

uu = importlib.import_module("lib.util")

class Mode(IntEnum):
    CREATE = 1
    APPEND = 2

    def __repr__(self):
        return self.name[0]

    def __str__(self):
        return self.name[0]

def performImport(cursor, inputPath, mode = Mode.CREATE):
    # tqdm.write(uu.color(f"[{filename}]", fg = 'green'))
    cin = CinTable(inputPath, level = CinTableParseLevel.Full)

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

        # filename = os.path.basename(inputPath)
        # if filename in HANS_TABLE:
        #     args = {'name': 'locale', 'value': 'zh-Hans'}
        #     cursor.execute(query, args)

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
    if mode == Mode.CREATE:
        cursor.execute("CREATE UNIQUE INDEX keydef_index ON keydef (key)")

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

        cin = CinTable(path, level = CinTableParseLevel.Full)

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
        # cursor.execute(f"CREATE UNIQUE INDEX `{keydefTableName}_index` ON keydef (key)")
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
    argParser.add_argument('-e', '--plugin', choices=['array', 'bossy'], help='plugin')
    argParser.add_argument('-v', '--validate', action='store_true', help='validate on/off')

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

    if args.validate:
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
