#!/usr/bin/env python
#
# version: 0.0.2
# autor: Ethan Liu
#
#

import argparse
import importlib
import sys, os
import re
import json, sqlite3
from tqdm import tqdm
# from time import sleep

uu = importlib.import_module("lib.util")

cwd = uu.dir(__file__ + "/../")

def testKeyboard():
    pass

def testTable():
    jsonFilePath = f"{cwd}/DataTables.json"
    file = open(jsonFilePath, 'r')
    data = json.load(file)
    file.close()

    version = data["version"] or 'missing';
    print(f"version: {version}")
    for item in data["datatables"]:
        dbPath = item['db'] or ''
        if not dbPath:
            print(f"{uu.color('[error]', fg = 'red')} db path not found")

        print(f"{uu.color('[file]', fg = 'green')} {item['db']}");
        db = sqlite3.connect(dbPath)
        cursor = db.cursor()

        # info
        print(f"[info]")
        cursor.execute("SELECT `name`, `value` FROM `info` ")
        result = cursor.fetchall()
        for item in result:
            print(f"{item[0]} = {item[1]}")

        # keyname
        cursor.execute("SELECT `key`, `value` FROM `keyname` ")
        result = cursor.fetchall()
        print(f"[keyname]")
        for item in result:
            print(f"{item[0]} = {item[1]}", end = ', ')
        print("")

        cursor.execute("SELECT c.rowid, k.key, c.char FROM `entry` AS e LEFT JOIN `keydef` AS k ON (k.rowid = e.keydef_id) LEFT JOIN `chardef` AS c ON (c.rowid = e.chardef_id) WHERE 1 ORDER BY RANDOM() LIMIT 10")
        result = cursor.fetchall()
        print(f"[entry]")
        for item in result:
            keydef = item[1] or ''
            chardef = item[2] or ''
            print(f"{chardef}\t{keydef}")

        db.close()
        # return

def testLexicon():
    jsonFilePath = f"{cwd}/Lexicon.json"
    file = open(jsonFilePath, 'r')
    data = json.load(file)
    file.close()

    version = data["version"] or 'missing';
    print(f"version: {version}")
    for item in data["resources"]:
        dbPath = item['db'] or ''
        if not dbPath:
            print(f"{uu.color('[error]', fg = 'red')} db path not found")

        print(f"{uu.color('[file]', fg = 'green')} {item['db']}");
        db = sqlite3.connect(dbPath)
        cursor = db.cursor()
        cursor.execute("SELECT `phrase`, `pinyin`, `weight` FROM `lexicon`, `pinyin` WHERE `lexicon`.`pinyin_id` = `pinyin`.`rowid` ORDER BY RANDOM() LIMIT 10")
        result = cursor.fetchall()
        for item in result:
            phrase = item[0] or ''
            pinyin = item[1] or ''
            weight = item[2] or 0
            print(f"\t{phrase} {pinyin} {weight}")
        db.close()

def main():
    argParser = argparse.ArgumentParser(description='Test')
    argParser.add_argument('-c', '--category', required = True, choices=['keyboard', 'lexicon', 'table'], help='Test target category')

    args = argParser.parse_args()
    # print(args, len(sys.argv))

    match args.category:
        case 'keyboard':
            testKeyboard()
        case 'table':
            testTable()
        case 'lexicon':
            testLexicon()

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
