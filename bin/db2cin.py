#!/usr/bin/env python
#
# version: 0.0.2
# autor: Ethan Liu
#
# convert cin table to sqlite db

import argparse
import importlib
import sys, os
import sqlite3
# from tqdm import tqdm

uu = importlib.import_module("lib.util")

def db2cin(args):

    db = sqlite3.connect(args.input)
    cursor = db.cursor()

    query = "SELECT count(*) FROM sqlite_master WHERE `type` = 'table' AND (`name` = 'info' OR `name` = 'keyname' OR `name` = 'chardef' OR `name` = 'keydef' OR `name` = 'entry')"
    result = uu.getOne(cursor, query)

    if result != 5:
        print(f'The file "{os.path.basename(args.input)}" is not a valid Frankie/OkidoKey db file')
        return

    contents = ""

    if args.header:
        with open(args.header, 'r') as fp:
            contents += fp.read()
            fp.close()
    else:
        # info
        query = "SELECT * FROM info"
        result = cursor.execute(query)
        for item in result:
            key = item[0] or ''
            value = item[1] or ''
            contents += f"%{key}\t{value}\n"
        # keyname
        query = "SELECT * FROM keyname"
        result = cursor.execute(query)
        contents += f"%keyname begin\n"
        for item in result:
            key = item[0] or ''
            value = item[1] or ''
            contents += f"{key}\t{value}\n"
        contents += f"%keyname end\n"
        pass

    # charset
    cursor.execute("SELECT c.rowid, k.key, c.char FROM `entry` AS e LEFT JOIN `keydef` AS k ON (k.rowid = e.keydef_id) LEFT JOIN `chardef` AS c ON (c.rowid = e.chardef_id) WHERE 1 ORDER BY k.rowid")
    result = cursor.fetchall()

    contents += f"%chardef begin\n"
    for item in result:
        key = item[1] or ''
        value = item[2] or ''
        contents += f"{key}\t{value}\n"
    contents += f"%chardef end\n"

    db.close()

    with open(args.output, 'w') as fp:
        fp.write(contents)
        fp.close()


def main():
    argParser = argparse.ArgumentParser(description='Convert sqlite db to cin table')
    argParser.add_argument('-i', '--input', type = str, required = True, help='The sqlite db file path')
    argParser.add_argument('-o', '--output', type = str, required = True, help='The cin table file path')
    argParser.add_argument('--header', type = str, help='The custom CIN table header file path (without charset tags)')

    args = argParser.parse_args()
    # print(args, len(sys.argv))
    # sys.exit(0)

    if not os.path.exists(args.input):
        print(f"File not found: {args.input}")
        sys.exit(0)

    if os.path.exists(args.output):
        # print(f"Remove existing file: {args.output}")
        os.remove(args.output)

    if args.header and not os.path.exists(args.header):
        print(f"File not found: {args.header}")
        sys.exit(0)

    db2cin(args)

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
