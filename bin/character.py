#!/usr/bin/env python
#
# version: 0.0.1
# autor: Ethan Liu
#
# generate resources form json
# /System/Library/Input Methods/CharacterPalette.app/Contents/Resources/CharacterDB.sqlite3
#

import argparse
import sys, os
import json
import sqlite3

def importkaomoji(cursor, path):
    file = open(path, 'r')
    data = json.load(file)
    file.close()

    cursor.execute("BEGIN TRANSACTION")
    for row in data['kaomoji']:
        cursor.execute("INSERT INTO kaomoji VALUES (?, ?)", (row, ""))
    cursor.execute("COMMIT TRANSACTION")

def importParentheses(cursor, path):
    file = open(path, 'r')
    data = json.load(file)
    file.close()

    cursor.execute("BEGIN TRANSACTION")
    for row in data['parentheses']:
        items = row.split('|')
        cursor.execute("INSERT INTO parentheses VALUES (?, ?)", (items[0], items[1]))
    cursor.execute("COMMIT TRANSACTION")

def importSymbol(cursor, path):
    file = open(path, 'r')
    data = json.load(file)
    file.close()

    # cursor.execute("SELECT uchr, info FROM unihan_dict WHERE info LIKE '%arrow%' AND info LIKE '%left%' LIMIT 10")
    # items = cursor.fetchall()

    cursor.execute("BEGIN TRANSACTION")
    for category in data["symbols"]:
        cursor.execute("INSERT INTO symbol_category VALUES (?)", (category,))
        categoryId = cursor.lastrowid
        for row in data["symbols"][category]:
            # info = row[1].split('|')
            try:
                cursor.execute("INSERT INTO symbol VALUES (?, ?, ?)", (categoryId, row[0], row[1]))
            except sqlite3.Error as e:
                print(e)
                # print(row)
    cursor.execute("COMMIT TRANSACTION")

def main():
    argParser = argparse.ArgumentParser(description='Pack utility')
    # argParser.add_argument('name', default='', choices=['kaomoji', 'parentheses', 'symbol'], help='package name')
    argParser.add_argument('path', default='tmp/Character.db', help='Output db file path')

    args = argParser.parse_args()
    # print(args)

    # CharacterDB
    # path = "tmp/Character.db"
    if os.path.exists(args.path):
        os.remove(args.path)

    db = sqlite3.connect(args.path)
    cursor = db.cursor()

    # schema
    cursor.execute("CREATE TABLE kaomoji (`char` CHAR(255) UNIQUE NOT NULL, `info` CHAR(255) default '')")
    cursor.execute("CREATE TABLE parentheses (`char` CHAR(255) UNIQUE NOT NULL, `info` CHAR(255) default '')")
    # cursor.execute("CREATE TABLE symbol (`char` CHAR(255) UNIQUE NOT NULL, `info` CHAR(255) default '')")
    cursor.execute("CREATE TABLE symbol_category (`name` CHAR(255) UNIQUE NOT NULL)")
    cursor.execute("CREATE TABLE symbol (`category_id` INTEGER NOT NULL, `char` CHAR(255) UNIQUE NOT NULL, `info` CHAR(255) default '')")

    importkaomoji(cursor, 'lexicon/kaomoji.json')
    importParentheses(cursor, 'lexicon/parentheses.json')
    importSymbol(cursor, 'lexicon/symbol.json')

    # if args.name == 'kaomoji':
    #     importkaomoji(cursor, 'lexicon/kaomoji.json')
    # elif args.name == 'parentheses':
    #     importParentheses(cursor, 'lexicon/parentheses.json')
    # elif args.name == 'symbol':
    #     # importSymbol(cursor, 'tmp/CharacterDB.sqlite3')
    #     importSymbol(cursor, 'lexicon/symbol.json')
    # else:
    #     argParser.print_usage()

    counters = [0, 0, 0]

    cursor.execute("SELECT COUNT(*) FROM kaomoji")
    counters[0] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM parentheses")
    counters[1] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM symbol")
    counters[2] = cursor.fetchone()[0]

    print(f"kaomoji: {counters[0]}")
    print(f"parentheses: {counters[1]}")
    print(f"symbol: {counters[2]}")

    db.commit()
    db.close()

    sys.exit(0)

if __name__ == "__main__":
    main()
