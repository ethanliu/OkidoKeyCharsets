#!/usr/bin/env python
#
# version: 0.1.0
# autor: Ethan Liu
#
# Unihan.db generator
# Unihan.db includes CJK radical stroke and weight...
#

import argparse
import importlib
import json
import sys, os
# import re
import csv
# import json
import sqlite3
import xml.etree.ElementTree as xet
from tqdm import tqdm
# from enum import IntEnum

uu = importlib.import_module("lib.util")
from lib.unihan import Classified, UnihanChar

basedir = os.path.normpath(os.path.join(os.path.dirname(__file__), os.path.pardir))


def importWeight(cursor):
    path = f"{basedir}/rawdata/McBopomofo/Source/Data/phrase.occ"
    if not os.path.exists(path):
        sys.exit(f"File not found: {path}")

    contents = []
    # filename = os.path.basename(path)

    with open(path) as fp:
        reader = csv.reader(fp, delimiter = '\t')
        for chunk in uu.chunks(reader, max = 0):
            for row in tqdm(chunk, desc = f"Lexicon[Weight]", unit = 'MB', unit_scale = True, ascii = True):
                if not row or not len(row) == 2:
                    continue
                radical = uu.trim(row[0])
                weight = int(row[1])
                if len(radical) > 1 or weight < 1:
                    continue
                contents.append([radical, weight])
        fp.close()

    query1 = f"SELECT `rowid` FROM `radical` WHERE `radical` = :radical LIMIT 1"
    query2 = f"INSERT INTO `radical` (`radical`, `weight`, `score`, `classified`) VALUES (:radical, :weight, :score, :classified)"
    query3 = f"UPDATE `radical` SET `weight` = :weight WHERE rowid = :id"

    cursor.execute("BEGIN TRANSACTION")
    for item in contents:
        rowid = uu.getOne(cursor, query1, {"radical": item[0]})
        if not rowid:
            # ???: classified zero?
            # cursor.execute(query2, {"radical": item[0], "weight": item[1], "score": 1, "classified": Classified.Unclassified})
            # tqdm.write(f"Add new radical: {item[0]}")
            pass
        else:
            cursor.execute(query3, {"id": rowid, "weight": item[1]})
    cursor.execute("COMMIT TRANSACTION")

def importClassified(cursor):
    path = f"{basedir}/rawdata/Unihan/tca.csv"
    if not os.path.exists(path):
        sys.exit(f"File not found: {path}")

    query1 = "SELECT rowid FROM `radical` WHERE radical = :radical LIMIT 1"
    query2 = "UPDATE `radical` SET classified = :classified WHERE rowid = :id"

    cursor.execute("BEGIN TRANSACTION")
    with open(path) as fp:
        reader = csv.reader(fp, delimiter = ',')
        for rows in uu.chunks(reader, 100000):
            for row in tqdm(rows, unit = 'MB', unit_scale = True, ascii = True, desc = f"Classified"):
                if not row or not len(row) == 2:
                    continue
                # print(row)
                radical = uu.trim(row[0])
                category = row[1][:1]
                classified = Classified.fromCategory(category)
                # print(f"{radical} => {category} / {classified}")

                rowid = uu.getOne(cursor, query1, {"radical": radical})
                if not rowid:
                    tqdm.write(f"Radical not exists: {radical}/{category}")
                    continue
                # else:
                #     tqdm.write(f"Radical found: {radical}/{category}")

                cursor.execute(query2, {"classified": classified, "id": rowid})
        fp.close()
    cursor.execute("COMMIT TRANSACTION")

def importUnihanRadical(cursor, repo, namespace):
    query = "INSERT INTO `radical` (`radical`, `pinyin`, `definition`, `classified`, `score`, `stroke`, `weight`) VALUES (:radical, :pinyin, :definition, :classified, :score, :stroke, :weight)"

    cursor.execute("BEGIN TRANSACTION")

    for chunk in uu.chunks(repo.findall('ucd:char', namespace), max = 0):
        for child in tqdm(chunk, desc = f"Unihan[Radical]", unit = 'MB', unit_scale = True, ascii = True):
        # for child in tqdm(repo.findall('ucd:char', namespace), unit = 'MB', unit_scale = True, ascii = True, desc = f"Radical"):
        # for child in repo.findall('ucd:char', namespace):
            char = UnihanChar(child)

            params = {
                "radical": char.text,
                "pinyin": char.mandarin or None,
                "definition": char.definition or None,
                "classified": char.classified,
                "score": char.score,
                "stroke": char.stroke,
                "weight": 0,
            }
            cursor.execute(query, params)

    cursor.execute("COMMIT TRANSACTION")

def importUnihanLocale(cursor, repo, namespace, table):
    query1 = "SELECT `rowid` FROM `radical` WHERE `radical` = :radical LIMIT 1"
    query2 = f"INSERT INTO `{table}` (`hant_id`, `hans_id`) VALUES (:hant_id, :hans_id)"

    if table == "t2s":
        target = "simplifiedVariant"
        radical_name = "hant_id"
        target_name = "hans_id"
    else:
        target = "traditionalVariant"
        radical_name = "hans_id"
        target_name = "hant_id"

    cursor.execute("BEGIN TRANSACTION")
    for chunk in uu.chunks(repo.findall('ucd:char', namespace), max = 0):
        for child in tqdm(chunk, desc = f"Unihan[{table}]", unit = 'MB', unit_scale = True, ascii = True):
            char = UnihanChar(child)
            variants = getattr(char, target)
            if not variants:
                continue

            radical_id = uu.getOne(cursor, query1, {"radical": char.text})
            if not radical_id:
                tqdm.write(f"Radical Not found: {char.text}")
                continue

            for variant in variants:
                target_id = uu.getOne(cursor, query1, {"radical": variant})
                if not target_id:
                    tqdm.write(f"Radical Not found: {variant}")
                    continue
                cursor.execute(query2, {radical_name: radical_id, target_name: target_id})
    cursor.execute("COMMIT TRANSACTION")

def importTongwenLocale(cursor, table, dir):
    def _import(path):
        query1 = "SELECT `rowid` FROM `radical` WHERE `radical` = :radical LIMIT 1"
        query2 = f"INSERT INTO `{table}` (`hans_id`, `hant_id`) VALUES (:hans_id, :hant_id)"
        prefix = f"Tongwen[{table}]"
        if table == "t2s":
            radical_name = "hant_id"
            target_name = "hans_id"
        else:
            radical_name = "hans_id"
            target_name = "hant_id"
        with open(path, 'r') as file:
            data = json.load(file)
            cursor.execute("BEGIN TRANSACTION")
            for key, value in tqdm(data.items(), desc = prefix, unit = 'MB', unit_scale = True, ascii = True):
                # print(f"{key} => {value}")
                radical_id = uu.getOne(cursor, query1, {"radical": key})
                target_id = uu.getOne(cursor, query1, {"radical": value})
                if not radical_id or not target_id:
                    tqdm.write(f"{prefix} Radical not found: {key} => {value}")
                    continue
                cursor.execute(query2, {radical_name: radical_id, target_name: target_id})
            cursor.execute("COMMIT TRANSACTION")
    _import(f"{dir}/{table}-char.json")
    # _import(f"{dir}/s2t-phrase.json")

def importUnihan(cursor, task):
    path = f"{basedir}/rawdata/Unihan/ucd.unihan.flat.xml"
    namespace = {
        'ucd': 'http://www.unicode.org/ns/2003/ucd/1.0',
    }
    root = xet.parse(path).getroot()
    repo = root.find('ucd:repertoire', namespace)

    if task == "radical":
        importUnihanRadical(cursor, repo, namespace)
    else:
        importUnihanLocale(cursor, repo, namespace, task)


def importTongwen(cursor, task):
    dir = f"{basedir}/rawdata/tongwen-core/dictionaries/"
    importTongwenLocale(cursor, task, dir)

def createDatabase(path):
    if os.path.isfile(path):
        os.remove(path)

    db = sqlite3.connect(path)
    cursor = db.cursor()

    # the radical based on unihan

    cursor.execute('''CREATE TABLE `radical` (
        `radical` CHAR(4) UNIQUE NOT NULL,
        `pinyin` CHAR(10) default NULL,
        `definition` TEXT default NULL,
        `classified` INTEGER default 0,
        `stroke` INTEGER default 0,
        `score` INTEGER default 0,
        `weight` INTEGER default 0
    )''')

    cursor.execute('''CREATE TABLE `t2s` (
        `hant_id` INTEGER default 0,
        `hans_id` INTEGER default 0
    )''')

    cursor.execute('''CREATE TABLE `s2t` (
        `hans_id` INTEGER default 0,
        `hant_id` INTEGER default 0
    )''')

    db.commit()
    db.close()

def test(cursor):
    print("test [t2s]")
    query = f"SELECT a.hant_id, a.hans_id, t.radical AS hant, s.radical AS hans FROM t2s AS a LEFT JOIN radical AS t ON (a.hant_id = t.rowid) LEFT JOIN radical AS s ON (a.hans_id = s.rowid) ORDER BY random() LIMIT 5"
    result = uu.getAll(cursor, query)
    for row in result:
        print(f"{row.get('hant')} => {row.get('hans')}")

    print("test [s2t]")
    query = f"SELECT a.hant_id, a.hans_id, t.radical AS hant, s.radical AS hans FROM s2t AS a LEFT JOIN radical AS t ON (a.hant_id = t.rowid) LEFT JOIN radical AS s ON (a.hans_id = s.rowid) ORDER BY random() LIMIT 5"
    result = uu.getAll(cursor, query)
    for row in result:
        print(f"{row.get('hans')} => {row.get('hant')}")


    list = '"麵", "面", "后", "後", "體", "園", "國", "国", "体", "园", "台", "臺", "颱"'

    print("test [t2s]")
    query = f'''SELECT
        t.radical AS hant,
        s.radical AS hans
    FROM t2s AS a
    LEFT JOIN radical AS t ON (t.rowid = a.hant_id)
    LEFT JOIN radical AS s ON (s.rowid = a.hans_id)
    WHERE hant IN ({list})
    ORDER BY hant
    '''
    result = uu.getAll(cursor, query)
    for row in result:
        print(f"{row.get('hant')} => {row.get('hans')}")

    print("test [s2t]")
    query = f'''SELECT
        t.radical AS hant,
        s.radical AS hans
    FROM s2t AS a
    LEFT JOIN radical AS t ON (t.rowid = a.hant_id)
    LEFT JOIN radical AS s ON (s.rowid = a.hans_id)
    WHERE hans IN ({list})
    ORDER BY hans
    '''
    result = uu.getAll(cursor, query)
    for row in result:
        print(f"{row.get('hans')} => {row.get('hant')}")


def main():
    argParser = argparse.ArgumentParser(description='Unihan Utility')
    # argParser.add_argument('-i', '--input', help='base dir of the repo')
    argParser.add_argument('-o', '--output', default='', help='output db path')
    args = argParser.parse_args()

    preferTonwen = False
    dryrun = False

    if not dryrun:
        createDatabase(args.output)

    db = sqlite3.connect(args.output)
    db.row_factory = uu.dict_factory
    # db.row_factory = sqlite3.Row
    cursor = db.cursor()

    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA journal_mode = MEMORY")

    if dryrun:
        test(cursor)
        sys.exit(0)

    importUnihan(cursor, "radical")
    if preferTonwen:
        importTongwen(cursor, "t2s")
        importTongwen(cursor, "s2t")
    else:
        importUnihan(cursor, "t2s")
        importUnihan(cursor, "s2t")
    # ## importClassified(cursor)
    importWeight(cursor)
    # test(cursor)

    # classfied, score not very useful at this moment
    # wipe them out but remain data struct
    cursor.execute("UPDATE `radical` SET `classified` = 0, `score` = 0")

    db.commit()
    cursor.execute('vacuum')
    # cursor.execute("CREATE INDEX `score_index` ON `radical` (score)")
    cursor.execute("CREATE INDEX `weight_index` ON `radical` (weight)")
    cursor.execute("CREATE INDEX `stroke_index` ON `radical` (stroke)")
    cursor.execute("CREATE INDEX `t2s_index` ON `t2s` (hant_id)")
    cursor.execute("CREATE INDEX `s2t_index` ON `s2t` (hans_id)")
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