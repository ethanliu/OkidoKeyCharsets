#!/usr/bin/env python
#
# version: 0.0.1
# autor: Ethan Liu
#
# convert cin table to sqlite db

import argparse
import importlib
import sys, os
import re
# import json
import sqlite3

uu = importlib.import_module("lib.util")

CIN_TAGS = [
    '%gen_inp',
    '%encoding',
    '%name',
    '%endkey',
    '%selkey',

    '%cname',
    '%ename',
    '%tcname',
    '%scname',
]

CIN_SECTION = [
    '%keyname',
    '%chardef',
]

	# private $propertyNames = ["%selkey", "%ename", "%cname", "%tcname", "%scname", "%endkey", "%encoding"];
	# private $mapNames = ["%keyname", "%chardef"];

def performImport(inputPath, outputPath):

    count = 0
    section = None

    db = sqlite3.connect(outputPath)
    cursor = db.cursor()

    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA journal_mode = MEMORY")

    cursor.execute("CREATE TABLE info (`name` CHAR(255) NOT NULL, `value` CHAR(255) default '')")
    cursor.execute("CREATE TABLE keyname (`key` CHAR(255) NOT NULL, `value` CHAR(255) default '')")
    cursor.execute("CREATE TABLE keydef (`key` CHAR(255) NOT NULL)")
    cursor.execute("CREATE TABLE chardef (`char` CHAR(255) NOT NULL)")
    cursor.execute("CREATE TABLE entry (`keydef_id` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL)")


	# if ($isArray) {
	# 	$db->exec("CREATE TABLE keydef_special (`key` CHAR(255) UNIQUE NOT NULL)");
	# 	$db->exec("CREATE TABLE keydef_shortcode (`key` CHAR(255) UNIQUE NOT NULL)");
	# 	$db->exec("CREATE TABLE entry_special (`keydef_special_id` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL)");
	# 	$db->exec("CREATE TABLE entry_shortcode (`keydef_shortcode_id` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL)");
	# }

    cursor.execute("BEGIN TRANSACTION")

    reader = open(inputPath, 'r')

    for row in reader:
        row = uu.trim(row, '#')
        if not row or row == '':
            continue

        items = re.split('[\s|\t]{1}', row, 1)
        if len(items) < 2:
            continue

        key = uu.trim(items[0])
        value = uu.trim(items[1])

        if key in CIN_SECTION:
            if section == key and value == 'end':
                print(f"End of Section: {section}")
                section = None
            else:
                # section = key[1:]
                section = key
                print(f"Begin of Section: {section}")
            continue

        if not section:
            if not key in CIN_TAGS:
                print(f"Invalid tag: {key}")
            else:
                print(f"[info] key: {key[1:]}, value: {value}")
                query = "SELECT rowid FROM info WHERE `name` = :name"
                args = {'name': key[1:]}
                result = uu.getOne(cursor, query, args)
                # print(result)

                if not result:
                    query = "INSERT INTO info (`name`, `value`) VALUES (:name, :value)"
                    args = {'name': key[1:], 'value': value}
                    cursor.execute(query, args)

                # cursor.execute("SELECT rowid FROM chardef WHERE char = ? LIMIT 1", (codes,))
                # # chardefId = cursor.fetchone()
                # result = cursor.fetchone()

                # if result:
                #     chardefId = result[0]
                # else:
                #     cursor.execute("INSERT INTO chardef VALUES (?)", (codes,))
                #     chardefId = cursor.lastrowid

            continue

        # print(f"[{section}] key: {key}, value: {value}")
        # query = "INSERT OR IGNORE INTO ..."

        if section == '%keyname':
            query = "SELECT rowid FROM keyname WHERE `key` = :key"
            args = {'key': key}
            result = uu.getOne(cursor, query, args)
            if result:
                print(f"[warn] duplicate keyname: {key}")
            else:
                query = "INSERT INTO keyname (`key`, `value`) VALUES (:key, :value)"
                args = {'key': key, 'value': value}
                cursor.execute(query, args)

        if section == '%chardef':
            query = "SELECT rowid FROM keydef WHERE `key` = :key"
            args = {'key': key}
            result = uu.getOne(cursor, query, args)
            if result:
                keydefId = result
            else:
                query = "INSERT INTO keydef (`key`) VALUES (:value)"
                args = {'value': key}
                cursor.execute(query, args)
                keydefId = cursor.lastrowid

            query = "SELECT rowid FROM chardef WHERE `char` = :char"
            args = {'char': value}
            result = uu.getOne(cursor, query, args)

            if result:
                chardefId = result
            else:
                query = "INSERT INTO chardef (`char`) VALUES (:value)"
                args = {'value': value}
                cursor.execute(query, args)
                chardefId = cursor.lastrowid

            query = "INSERT INTO entry (`keydef_id`, `chardef_id`) VALUES (:kid, :vid)"
            args = {'kid': keydefId, 'vid': chardefId}

            cursor.execute(query, args)

        # count += 1
        # if count > 100:
        #     break

    cursor.execute("COMMIT TRANSACTION")

    reader.close()

    db.commit()

    # index
    cursor.execute('vacuum')
    cursor.execute("CREATE UNIQUE INDEX info_index ON info (name)")
    cursor.execute("CREATE UNIQUE INDEX keyname_index ON info (name)")
    cursor.execute("CREATE UNIQUE INDEX keydef_index ON keydef (key)")
    cursor.execute("CREATE UNIQUE INDEX chardef_index ON chardef (char)")
    cursor.execute("CREATE INDEX entry_index ON entry (keydef_id, chardef_id)")

	# if ($isArray) {
	# 	$db->exec("CREATE UNIQUE INDEX keydef_special_index ON keydef_special (key)");
	# 	$db->exec("CREATE UNIQUE INDEX keydef_shortcode_index ON keydef_shortcode (key)");
	# 	$db->exec("CREATE INDEX entry_special_index ON entry_special (keydef_special_id, chardef_id)");
	# 	$db->exec("CREATE INDEX entry_shortcode_index ON entry_shortcode (keydef_shortcode_id, chardef_id)");
	# }



    # cursor.execute("SELECT COUNT(*) FROM chardef")
    # characterCounter = cursor.fetchone()[0]

    # cursor.execute("SELECT COUNT(*) FROM keydef")
    # keywordsCounter = cursor.fetchone()[0]

    db.close()

    print('fin.')

def main():
    argParser = argparse.ArgumentParser(description='Convert cin table to sqlite db file')
    argParser.add_argument('-i', '--input', type = str, required = True, help='The input file path of cin table file')
    argParser.add_argument('-o', '--output', type = str, required = True, help='The output file path')

    argParser.add_argument('--array-short', type = str, help='The input file path of array-shortcode.cin')
    argParser.add_argument('--array-sp', type = str, help='The input file path of array-special.cin')

    args = argParser.parse_args()
    # print(args, len(sys.argv))
    # sys.exit(0)

    if os.path.exists(args.output):
        print(f"Remove existing file: {args.output}")
        os.remove(args.output)

    if not os.path.exists(args.input):
        print(f"Input file not found: {args.input}")
        sys.exit(0)

    performImport(args.input, args.output);

    sys.exit(0)

if __name__ == "__main__":
    main()
