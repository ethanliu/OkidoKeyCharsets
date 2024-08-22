#!/usr/bin/env python
#
# version: 0.0.3
# autor: Ethan Liu
#
# generate resources form json
# /System/Library/Input Methods/CharacterPalette.app/Contents/Resources/CharacterDB.sqlite3
#

import argparse
import sys, os
import json
import sqlite3

def importSymbol(cursor, path):
    file = open(path, 'r')
    data = json.load(file)
    file.close()

    # cursor.execute("SELECT uchr, info FROM unihan_dict WHERE info LIKE '%arrow%' AND info LIKE '%left%' LIMIT 10")
    # items = cursor.fetchall()

    cursor.execute("BEGIN TRANSACTION")
    for category in data["category"]:
        cursor.execute("INSERT INTO category VALUES (?)", (category,))
        categoryId = cursor.lastrowid
        for row in data["symbol"][category]:
            # info = row[1].split('|')
            try:
                cursor.execute("INSERT INTO symbol VALUES (?, ?, ?)", (categoryId, row[0], row[1]))
            except sqlite3.Error as e:
                print(e)
                print(row)
    cursor.execute("COMMIT TRANSACTION")

def runTest(path):
    db = sqlite3.connect(path)
    cursor = db.cursor()

    prefix = "EXPLAIN QUERY PLAN "
    # prefix = ""

    tests = [
        "SELECT s.info FROM symbol AS s LEFT JOIN category AS c ON (c.rowid = s.category_id) WHERE 1 AND c.name = 'parentheses' AND char = '(' LIMIT 1",
        "SELECT s.char FROM symbol AS s LEFT JOIN category AS c ON (c.rowid = s.category_id) WHERE 1 AND c.name = 'kaomoji' ORDER BY s.rowid",
        "SELECT s.char FROM symbol AS s LEFT JOIN category AS c ON (c.rowid = s.category_id) WHERE 1 AND c.name != 'kaomoji' AND c.name = 'punctuation' OR s.info LIKE '%arrow%' OR s.info LIKE '%up%' ORDER BY s.rowid",
    ]

    # for index, code in enumerate(codes):
    for index, query in enumerate(tests):
        print(f"Test phase {index + 1}...")
        cursor.execute(prefix + query)
        result = cursor.fetchall()
        print(result)


    db.close()

def main():
    argParser = argparse.ArgumentParser(description = 'Character.db Utility')
    argParser.add_argument('--test', action = argparse.BooleanOptionalAction, help = 'Run test')
    argParser.add_argument('-i', '--input', type = str, help = 'The file path of symbol.json')
    argParser.add_argument('output', type = str, help = 'The output file path of Character.db')

    args = argParser.parse_args()
    # print(args)

    if args.test:
        if not os.path.exists(args.output):
            print(f"File not found: {args.output}")
            sys.exit(0)
        runTest(args.output)
        sys.exit(0)

    if not args.input or not os.path.exists(args.input):
        print(f"File not found: {args.input}")
        sys.exit(0)


    # CharacterDB
    # path = "tmp/Character.db"
    if os.path.exists(args.output):
        print(f"Remove existing file: {args.output}")
        os.remove(args.output)


    print(f"Generate new file: {args.output}")
    db = sqlite3.connect(args.output)
    cursor = db.cursor()

    # schema
    # cursor.execute("CREATE TABLE category (`name` VARCHAR(255) UNIQUE NOT NULL)")
    # cursor.execute("CREATE TABLE symbol (`category_id` INTEGER NOT NULL, `char` VARCHAR(255) UNIQUE NOT NULL, `info` VARCHAR(255) default '')")
    cursor.execute("CREATE TABLE category (`name` VARCHAR(255) NOT NULL)")
    cursor.execute("CREATE TABLE symbol (`category_id` INTEGER NOT NULL, `char` VARCHAR(255) NOT NULL, `info` VARCHAR(255) default '')")

    print(f"Importing file: {args.input}")
    importSymbol(cursor, args.input)

    db.commit()

    # index
    cursor.execute('vacuum')
    cursor.execute("CREATE UNIQUE INDEX category_name_index ON category (name)")
    cursor.execute("CREATE UNIQUE INDEX symbol_char_index ON symbol (char)")

    counter = 0
    cursor.execute("SELECT COUNT(*) FROM symbol")
    counter = cursor.fetchone()[0]

    # print(f"kaomoji: {counters[0]}")
    # print(f"parentheses: {counters[1]}")
    print(f"Total rows: {counter}")


    db.close()

    sys.exit(0)

if __name__ == "__main__":
    main()
