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
from lib.cintable import CinTable, Block
# from time import sleep

uu = importlib.import_module("lib.util")

class Mode(IntEnum):
    CREATE = 1
    APPEND = 2

    def __repr__(self):
        return self.name[0]

    def __str__(self):
        return self.name[0]

def perform_import(cursor, input_path, mode = Mode.CREATE):
    # tqdm.write(uu.color(f"[{filename}]", fg = 'green'))
    cin = CinTable(input_path, [Block.Chardef])

    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA journal_mode = MEMORY")
    cursor.execute("BEGIN TRANSACTION")

    if mode == Mode.CREATE:
        query = "INSERT OR IGNORE INTO `info` (`name`, `value`) VALUES (:name, :value)"
        for key in cin.meta:
            value = cin.meta[key]
            if value:
                args = {'name': key, 'value': value}
                cursor.execute(query, args)

        query = "INSERT OR IGNORE INTO `keyname` (`key`, `value`) VALUES (:name, :value)"
        for key in cin.keyname:
            args = {'name': key, 'value': cin.keyname[key]}
            cursor.execute(query, args)

    query1 = "INSERT OR IGNORE INTO `keydef` (`key`) VALUES (:value)"
    # query2 = "SELECT `rowid` FROM `keydef` WHERE `key` = :value LIMIT 1"
    query3 = "INSERT OR IGNORE INTO `chardef` (`char`) VALUES (:value)"
    # query4 = "SELECT `rowid` FROM `chardef` WHERE `char` = :value LIMIT 1"
    # query5 = "INSERT OR IGNORE INTO `entry` (`keydef_id`, `chardef_id`) VALUES (:kid, :cid)"
    query6 = "INSERT INTO `entry` (`keydef_id`, `chardef_id`) SELECT k.rowid AS kid, c.rowid AS cid FROM `keydef` AS k, `chardef` AS c WHERE 1 AND k.key = :key AND c.char = :value ORDER BY c.rowid ASC"

    for item in tqdm(cin.chardef, unit = 'MB', unit_scale = True, ascii = True, desc = f"{cin.get_name()}[1]"):
        # print(f"{item[0]} => {item[1]}")
        key = item[0]
        value = item[1]

        # old school way, one by one
        # bossy.cin took 3s

        # # keydef
        # args = {'value': key}
        # cursor.execute(query1, args)
        # keydefId = uu.db_get_one(cursor, query2, args)

        # # chardef
        # args = {'value': value}
        # cursor.execute(query3, args)
        # chardefId = uu.db_get_one(cursor, query4, args)

        # #entry pivot
        # args = {'kid': keydefId, 'cid': chardefId}
        # cursor.execute(query5, args)

        # v2, keydef and chardef
        cursor.execute(query1,  {'value': key})
        cursor.execute(query3, {'value': value})

    # v2: entry
    for item in tqdm(cin.chardef, unit = 'MB', unit_scale = True, ascii = True, desc = f"{cin.get_name()}[2]"):
        key = item[0]
        value = item[1]
        cursor.execute(query6, {'key': key, 'value': value})

    cursor.execute("COMMIT TRANSACTION")
    cursor.execute('VACUUM')
    if mode == Mode.CREATE:
        cursor.execute("CREATE UNIQUE INDEX keydef_index ON keydef (key)")

def validate(cursor):
    cursor.execute("SELECT key, value FROM `keyname` ORDER BY rowid")
    result = cursor.fetchall()
    for item in tqdm(result, unit_scale = True, ascii = True, desc = f"Validation"):
        query = "SELECT COUNT(rowid) FROM `keydef` WHERE key LIKE :key"
        check = uu.db_get_one(cursor, query, {'key': f"%{item[0]}%"})
        if not check or check <= 1:
            tqdm.write(f"[?] keyname: {item[0]} ({item[1]}) never or rarely used")

def plugin_array(cursor, input_path):
    cin = CinTable(input_path, [Block.Shortcode, Block.Special])
    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA journal_mode = MEMORY")
    cursor.execute("BEGIN TRANSACTION")

    for category in cin.extra:
        rows = cin.extra[category]
        if not rows:
            # tqdm.write(f"No data for {category}")
            continue

        keydef_table_name = f"keydef_{category}"
        entry_table_name = f"entry_{category}"
        entry_keydef_column_name = f"keydef_{category}_id"

        query1 = f"INSERT OR IGNORE INTO `{keydef_table_name}` (`key`) VALUES (:value)"
        query3 = "INSERT OR IGNORE INTO `chardef` (`char`) VALUES (:value)"
        query6 = f"INSERT OR IGNORE INTO `{entry_table_name}` (`{entry_keydef_column_name}`, `chardef_id`) SELECT k.rowid AS kid, c.rowid AS cid FROM `{keydef_table_name}` AS k, `chardef` AS c WHERE 1 AND k.key = :key AND c.char = :value ORDER BY c.rowid ASC"

        cursor.execute(f"CREATE TABLE {keydef_table_name} (`key` VARCHAR(255) UNIQUE NOT NULL)")
        cursor.execute(f"CREATE TABLE {entry_table_name} (`{entry_keydef_column_name}` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL)")

        for item in tqdm(rows, unit = 'MB', unit_scale = True, ascii = True, desc = f"{category}[1]"):
            key = item[0]
            value = item[1]
            cursor.execute(query1,  {'value': key})
            cursor.execute(query3, {'value': value})
        for item in tqdm(rows, unit = 'MB', unit_scale = True, ascii = True, desc = f"{category}[2]"):
            key = item[0]
            value = item[1]
            cursor.execute(query6, {'key': key, 'value': value})

    # commit
    cursor.execute("COMMIT TRANSACTION")
    cursor.execute('VACUUM')

def plugin_bossy(cursor):
    query = "UPDATE `info` SET value = :value WHERE `name` = :name"
    args = {'name': 'ename', 'value': "Bossy"}
    cursor.execute(query, args)
    args = {'name': 'cname', 'value': "謥蝦米"}
    cursor.execute(query, args)
    pass

def main():
    arg_reader = argparse.ArgumentParser(description='Convert cin table to sqlite db file')
    arg_reader.add_argument('-i', '--input', type = str, required = True, nargs = '+', help='The cin table file(s), the first one would be the major table for information')
    arg_reader.add_argument('-o', '--output', type = str, required = True, help='The sqlite file path')
    # argParser.add_argument('-t', '--test', type = str, help='The database file path')
    # argParser.add_argument('--header', type = str, help='The custom CIN table header file path')
    arg_reader.add_argument('-e', '--plugin', choices=['array', 'bossy'], help='plugin')
    arg_reader.add_argument('-v', '--validate', action='store_true', help='validate on/off')

    args = arg_reader.parse_args()
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
    cursor.execute("CREATE TABLE info (`name` VARCHAR(255) UNIQUE NOT NULL, `value` VARCHAR(255) default '')")
    cursor.execute("CREATE TABLE keyname (`key` VARCHAR(255) UNIQUE NOT NULL, `value` VARCHAR(255) default '')")
    cursor.execute("CREATE TABLE keydef (`key` VARCHAR(255) UNIQUE NOT NULL)")
    cursor.execute("CREATE TABLE chardef (`char` VARCHAR(255) UNIQUE NOT NULL)")
    cursor.execute("CREATE TABLE entry (`keydef_id` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL, UNIQUE(`keydef_id`, `chardef_id`) ON CONFLICT IGNORE)")

    mode = Mode.CREATE
    for index, path in enumerate(args.input):
        if index > 0:
            mode = Mode.APPEND
        # print(f"{index}: {mode} {path}")
        perform_import(cursor, path, mode)
        db.commit()

    if args.plugin:
        match args.plugin:
            case "array":
                plugin_array(cursor, args.input[0])
            case "bossy":
                plugin_bossy(cursor)
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
