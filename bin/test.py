#!/usr/bin/env python
#
# version: 0.0.2
# autor: Ethan Liu
#
#

import sys
import os
import glob
# import re
import sqlite3
from lib.util import db_get_all, db_get_one
from pypinyin import lazy_pinyin, Style

DIST_DIR = "dist/queue"

PASS = "👍"
FAIL = "❌"

def run_table_test():
    print("--- Table Test ---")

    query1 = "SELECT * FROM `info`"
    query2 = "SELECT * from `keyname`"
    query3 = f'''
SELECT
	e.keydef_id,
	k.key,
    e.chardef_id,
	c.char
FROM
	keydef AS k, entry AS e
LEFT JOIN chardef AS c ON (c.rowid = e.chardef_id)
WHERE 1
	AND k.rowid = e.keydef_id
ORDER BY random()
LIMIT 0, 10
    '''
    paths = sorted(glob.glob(f"{DIST_DIR}/table/*.db"), key=os.path.basename)
    for path in paths:
        db = sqlite3.connect(path)
        cursor = db.cursor()
        cursor.execute('VACUUM')

        filename = os.path.basename(path)
        message = ""

        # test 1
        result = db_get_all(cursor, query1)
        if not result:
            message += f"{FAIL} missing info\n"

        # test 2
        result = db_get_all(cursor, query2)
        if not result:
            message += f"{FAIL} missing keyname\n"

        # test 3
        result = db_get_all(cursor, query3)
        if not result:
            message += f"{FAIL} missing radicals\n"

        if message:
            print(f"{FAIL} {filename}")
            print(message)
        else:
            print(f"{PASS} {filename}")

        db.close()

def run_lexicon_test():
    print("--- Lexicon Test ---")
    query1 = "SELECT * from `lexicon` ORDER BY random() LIMIT 0, 10"

    paths = sorted(glob.glob(f"{DIST_DIR}/lexicon/*.db"), key=os.path.basename)
    for path in paths:
        db = sqlite3.connect(path)
        cursor = db.cursor()
        cursor.execute('VACUUM')

        filename = os.path.basename(path)
        message = ""

        # test 1
        result = db_get_all(cursor, query1)
        if not result:
            message += f"{FAIL} emtpy content?\n"

        if message:
            print(f"{FAIL} {filename}")
            print(message)
        else:
            print(f"{PASS} {filename}")

        db.close()

def playground():
    text = "知吃日師勢紙資此茲一雨吳雞啊鵝衣儿安凹喔唉吁西吸七"
    for cc in text:
        pp = lazy_pinyin(cc, strict=False, errors='ignore', style=Style.NORMAL)
        print(f"{cc} => {pp}")

def main():
    print("Run test")
    # run_table_test()
    # run_lexicon_test()
    pass

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

