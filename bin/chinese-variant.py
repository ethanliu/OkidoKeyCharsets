#!/usr/bin/env python
#
# version: 0.0.1
# autor: Ethan Liu
#
# ChineseVariant.db generator

import argparse
import csv
# import importlib
import sys, os
import json
import sqlite3
from tqdm import tqdm

# uu = importlib.import_module("lib.util")

def performImport(cursor, inputPath):
    filename = os.path.basename(inputPath)
    csvfile = open(inputPath, 'r')
    reader = csv.reader(csvfile, delimiter = '\t', quotechar = None)
    # reader = csv.DictReader(csvfile, fieldnames={'phrase,', 'weight', 'pinyin'})

    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA journal_mode = MEMORY")
    cursor.execute("BEGIN TRANSACTION")

    for row in tqdm(reader, unit = 'MB', unit_scale = True, ascii = True, desc = f"Import {filename}"):
        phrase = (row[0] or '').strip()
        weight = row[1] or 0
        pinyin = (row[2] or '').strip()
        pinyin_id = 0

        if not phrase:
            continue

        if pinyin:
            query = "INSERT OR IGNORE INTO pinyin (pinyin) VALUES (:pinyin)"
            args = {'pinyin': pinyin}
            cursor.execute(query, args)
            pinyin_id = cursor.lastrowid

        query = "INSERT OR IGNORE INTO lexicon (phrase, weight, pinyin_id) VALUES (:phrase, :weight, :pinyin_id)"
        args = {'phrase': phrase, 'weight': weight, 'pinyin_id': pinyin_id}
        cursor.execute(query, args)

    # reader.close()
    csvfile.close()

    cursor.execute("COMMIT TRANSACTION")
    cursor.execute('VACUUM')

def tongwen2db(cursor, inputPath):
    categories = ["s2t", "t2s"]
    tableNames = {"s2t": "char_hans", "t2s": "char_hant"}

    cursor.execute("BEGIN TRANSACTION")

    for category in categories:
        path = f"{inputPath}/{category}-char.json"
        file = open(path, 'r')
        data = json.load(file)
        file.close()

        tableName = tableNames[category]
        query = f"INSERT INTO `{tableName}` VALUES (:k, :v)"
        for k, v in tqdm(data.items(), unit = 'MB', unit_scale = True, ascii = True, desc = f"Import {category}"):
        # for k, v in data.items():
            cursor.execute(query, {'k': k, 'v': v})

    cursor.execute("COMMIT TRANSACTION")
    cursor.execute('vacuum')


def main():
    argParser = argparse.ArgumentParser(description='ChineseVariant.db generator')
    argParser.add_argument('-i', '--input', type = str, required = True, help='The tongwen repo dictionary folder path')
    argParser.add_argument('-o', '--output', type = str, required = True, help='The sqlite file path')

    args = argParser.parse_args()
    # print(args, len(sys.argv))
    # sys.exit(0)

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

    cursor.execute("CREATE TABLE char_hans (`hans` CHAR(255) UNIQUE NOT NULL, `hant` CHAR(255) default '')")
    cursor.execute("CREATE TABLE char_hant (`hant` CHAR(255) UNIQUE NOT NULL, `hans` CHAR(255) default '')")
    # cursor.execute("CREATE TABLE phrase_hans (`hans` CHAR(255) UNIQUE NOT NULL, `hant` CHAR(255) default '')")
    # cursor.execute("CREATE TABLE phrase_hant (`hant` CHAR(255) UNIQUE NOT NULL, `hans` CHAR(255) default '')")

    cursor.execute('CREATE UNIQUE INDEX char_hans_index ON char_hans (hans)')
    cursor.execute('CREATE UNIQUE INDEX char_hant_index ON char_hant (hant)')

    tongwen2db(cursor, args.input)
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
