#!/usr/bin/env python
#
# autor: Ethan Liu
#
# mega lexicon

import argparse
# import importlib
import sys, os
import csv
import re
import sqlite3
from tqdm import tqdm
from lib.util import chunks, db_get_all

def build(inputs, output):
    print("Build mega lexicon db")
    superdb = sqlite3.connect(output)
    super_cursor = superdb.cursor()

    super_cursor.execute("CREATE TABLE `source` (`name` VARCHAR(255) NOT NULL)")
    super_cursor.execute("CREATE TABLE `lexicon` (`phrase` TEXT NOT NULL, `pinyin` VARCHAR(255) DEFAULT NULL, `weight` INTEGER DEFAULT 0, `source_id` INTEGER DEFAULT 0, UNIQUE(`phrase`))")
    super_cursor.execute("CREATE INDEX IF NOT EXISTS `phrase_index` ON `lexicon` (phrase, weight)")

    query1 = """
        INSERT INTO lexicon (phrase, weight, source_id)
        VALUES (:phrase, :weight, :source_id)
        ON CONFLICT(phrase) DO UPDATE SET weight = MAX(weight, :weight);
    """
    query2 = "SELECT phrase, weight FROM lexicon WHERE weight > 0 ORDER BY weight DESC"

    for input in inputs:
        source_name = os.path.basename(input)
        super_cursor.execute("INSERT INTO source (name) VALUES (:name)", {'name': source_name})
        source_id = super_cursor.lastrowid
        print(f"#{source_id} {source_name}")

        _db = sqlite3.connect(input)
        _cursor = _db.cursor()
        data = db_get_all(_cursor, query2)
        for item in data:
            # print(item)
            super_cursor.execute(query1, {'phrase': item[0], 'weight': item[1], 'source_id': source_id})
        _db.close()

    superdb.commit()
    # super_cursor.execute('VACUUM')
    superdb.close()


def apply_unihan(input, output):
    if not os.path.exists(input) or not os.path.exists(output):
        print(f"File not found")
        return

    print("Apply mega lexicon db to unihan")

    db = sqlite3.connect(output)
    # db.row_factory = dict_factory
    cursor = db.cursor()

    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA journal_mode = MEMORY")

    cursor.execute(f"ATTACH DATABASE '{input}' as megadb")
    cursor.execute("""
        UPDATE radical
        SET weight = (SELECT weight FROM megadb.lexicon WHERE megadb.lexicon.phrase = radical.radical)
        WHERE EXISTS (SELECT 1 FROM megadb.lexicon WHERE megadb.lexicon.phrase = radical.radical)
    """)

    db.commit()
    cursor.execute("DETACH DATABASE megadb")
    db.close()


def apply_lexicon(input, output):
    if not os.path.exists(input) or not os.path.exists(output):
        print(f"File not found")
        return

    dbname = os.path.basename(output)
    print(f"Apply mega lexicon db to lexicon {dbname}")

    db = sqlite3.connect(output)
    # db.row_factory = dict_factory
    cursor = db.cursor()

    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA journal_mode = MEMORY")

    cursor.execute(f"ATTACH DATABASE '{input}' as megadb")
    cursor.execute("""
        UPDATE main.lexicon
        SET weight = (SELECT weight FROM megadb.lexicon WHERE megadb.lexicon.phrase = main.lexicon.phrase)
        WHERE EXISTS (SELECT 1 FROM megadb.lexicon WHERE megadb.lexicon.phrase = main.lexicon.phrase)
    """)

    db.commit()
    cursor.execute("DETACH DATABASE megadb")
    db.close()


def main():
    arg_reader = argparse.ArgumentParser(description='Convert lexicon csv to sqlite db file')
    arg_reader.add_argument('-i', '--input', nargs="+", required=True, help='The lexicon csv file path')
    arg_reader.add_argument('-o', '--output', type=str, required=True, help='The sqlite file path')

    arg_reader.add_argument('--build', default=False, action=argparse.BooleanOptionalAction, help='create mega dict')
    arg_reader.add_argument('--apply', type=str, required=False, help='The lexicon csv file path')

    args = arg_reader.parse_args()
    # print(args, len(sys.argv))
    # sys.exit(0)

    if args.build:
        build(args.input, args.output)
    elif args.apply:
        if args.apply == "unihan":
            apply_unihan(args.input[0], args.output)
        elif args.apply == "lexicon":
            apply_lexicon(args.input[0], args.output)

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
