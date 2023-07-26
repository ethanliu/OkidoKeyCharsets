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
import sys, os
# import re
import csv
# import json
import sqlite3
import xml.etree.ElementTree as xet
from tqdm import tqdm

uu = importlib.import_module("lib.util")

basedir = os.path.normpath(os.path.join(os.path.dirname(__file__), os.path.pardir))
consoleBufferSize = -100

#	kCompatibilityVariant
#	kIICore
#	kIRG_GSource 電腦用中文字型與字碼對照表
#	kIRG_HSource
#	kIRG_JSource  character in hexadecimal or decimal
#	kIRG_KPSource North Korea
#	kIRG_KSource Korean History
#	kIRG_MSource Macao
#	kIRG_SSource 大正新脩大藏經
#	kIRG_TSource 教育部
#	kIRG_UKSource
#	kIRG_USource
#	kIRG_VSource
#	kRSUnicode
#	kTotalStrokes

# 3.1 IRG Sources
# Among the few normative parts of the Unihan database, and the most exhaustively checked fields, are the IRG source fields: kIRG_GSource (China and Singapore), kIRG_HSource (Hong Kong SAR), kIRG_JSource (Japan), kIRG_KPSource (North Korea), kIRG_KSource (South Korea), kIRG_MSource (Macao SAR), kIRG_SSource (SAT Daizōkyō Text Database Committee), kIRG_TSource (TCA), kIRG_UKSource (UK), kIRG_USource (UTC), and kIRG_VSource (Vietnam).

# def importStroke(cursor):
#     path = f"{basedir}/rawdata/Unihan/Unihan_IRGSources.txt"
#     if not os.path.exists(path):
#         sys.exit(f"File not found: {path}")

#     contents = []
#     filename = os.path.basename(path)
#     reader = open(path, 'r')

#     for row in tqdm(reader.readlines(), unit = 'MB', unit_scale = True, ascii = True, desc = f"[{filename}]"):
#         row = uu.trim(row, '#')
#         if not row or row == '':
#             continue
#         if consoleBufferSize > 0 and len(contents) > consoleBufferSize:
#             break
#         items = re.split('[\s\t]{1}', row)
#         if items[1] == "kTotalStrokes":
#             radical = chr(int(items[0][2:], 16))
#             stroke = int(items[2])
#             # contents.append({
#             #     "radical": radical,
#             #     "stroke": stroke,
#             # })
#             contents.append([radical, stroke])

#     reader.close()

#     query1 = f"SELECT `rowid` FROM `unihan` WHERE `radical` = :radical LIMIT 1"
#     query2 = f"INSERT INTO `unihan` (`radical`, `stroke`) VALUES (:radical, :stroke)"
#     query3 = f"UPDATE `unihan` SET `stroke` = :stroke WHERE rowid = :id"

#     cursor.execute("BEGIN TRANSACTION")
#     for item in contents:
#         rowid = uu.getOne(cursor, query1, {"radical": item[0]})
#         if not rowid:
#             cursor.execute(query2, {"radical": item[0], "stroke": item[1]})
#         else:
#             cursor.execute(query3, {"id": rowid, "stroke": item[1]})
#     cursor.execute("COMMIT TRANSACTION")

# This file contains data on the following fields from the Unihan database:
#	kSemanticVariant
#	kSimplifiedVariant
#	kSpecializedSemanticVariant
#	kSpoofingVariant
#	kTraditionalVariant
#	kZVariant
#
# For details on the file format, see http://www.unicode.org/reports/tr38/
# def importVariant(cursor):

#     def _getColumns(category):
#         radicalColumn = None
#         variantColumn = None
#         match category:
#             case "kSemanticVariant":
#                 # 同義字，如: U+514E 兎 and U+5154 兔
#                 radicalColumn = "_skip"
#                 pass
#             case "kSimplifiedVariant":
#                 radicalColumn = "zh_Hant_TW"
#                 variantColumn = "zh_Hans_CN"
#             case "kSpecializedSemanticVariant":
#                 # 同義字，取自不同字典
#                 radicalColumn = "_skip"
#                 pass
#             case "kSpoofingVariant":
#                 # 形狀類似，易混淆的字體，如: U+672C 本 and U+5932 夲; U+520A 刊 and U+520B 刋.
#                 radicalColumn = "_skip"
#                 pass
#             case "kTraditionalVariant":
#                 radicalColumn = "zh_Hans_CN"
#                 variantColumn = "zh_Hant_TW"
#             case "kZVariant":
#                 # 同字/同形，但不同編碼
#                 radicalColumn = "_skip"
#                 pass
#             case _:
#                 print(f"unknown category: {category}")
#                 pass
#         return (radicalColumn, variantColumn)


#     path = f"{basedir}/rawdata/Unihan/Unihan_Variants.txt"
#     if not os.path.exists(path):
#         sys.exit(f"File not found: {path}")

#     debugBuffer = ""
#     filename = os.path.basename(path)
#     reader = open(path, 'r')

#     cursor.execute("BEGIN TRANSACTION")

#     for row in tqdm(reader.readlines(), unit = 'MB', unit_scale = True, ascii = True, desc = f"[{filename}]"):
#         row = uu.trim(row, '#')
#         if not row or row == '':
#             continue
#         if consoleBufferSize > 0 and len(debugBuffer) > consoleBufferSize:
#             break
#         items = re.split('[\s\t]{1}', row)

#         radical = items.pop(0)
#         radical = chr(int(radical[2:], 16))
#         category = items.pop(0)

#         yVariants = []
#         for item in items:
#             _items = item.split('<')
#             _radical = chr(int(_items[0][2:], 16))
#             if len(_items) > 1:
#                 _category = _items[1]
#                 # print(f"{item} => {_radical} / {_category}")
#                 yVariants.append([_radical, _category])
#             else:
#                 # print(f"{item} => {_radical}")
#                 yVariants.append([_radical, ''])

#         # query = "SELECT rowid FROM `unihan` WHERE radical = :radical";
#         # rowid = uu.getOne(cursor, query, {"radical": radical})

#         for y in yVariants:
#             _from, _to = _getColumns(category)

#             if _from == "_skip":
#                 continue

#             if _from and _to:
#                 # print(f"{category}/{y[1]} => UPDATE `unihan` SET {_from} = {radical}, {_to} = {y[0]} WHERE `radical` = {radical}")
#                 cursor.execute(f"UPDATE `unihan` SET {_from} = :from, {_to} = :to WHERE `radical` = :radical", {"radical": radical, "from": radical, "to": y[0]})
#                 pass
#             else:
#                 print(f"Unknown column: {category} {radical}")
#                 # print(y)
#                 pass

#         debugBuffer += "."

#     cursor.execute("COMMIT TRANSACTION")
#     reader.close()
#     pass

def importWeight(cursor):
    path = f"{basedir}/rawdata/McBopomofo/Source/Data/phrase.occ"
    if not os.path.exists(path):
        sys.exit(f"File not found: {path}")

    contents = []
    # filename = os.path.basename(path)

    with open(path) as fp:
        reader = csv.reader(fp, delimiter = '\t')
        for rows in uu.chunks(reader, 100000):
            for row in tqdm(rows, unit = 'MB', unit_scale = True, ascii = True, desc = f"Weight"):
                if not row or not len(row) == 2:
                    continue
                if consoleBufferSize > 0 and len(contents) > consoleBufferSize:
                    break
                radical = uu.trim(row[0])
                weight = int(row[1])
                if len(radical) > 1 or weight < 1:
                    continue
                contents.append([radical, weight])
        fp.close()

    query1 = f"SELECT `rowid` FROM `unihan` WHERE `radical` = :radical LIMIT 1"
    query2 = f"INSERT INTO `unihan` (`radical`, `weight`, `score`) VALUES (:radical, :weight, :score)"
    query3 = f"UPDATE `unihan` SET `weight` = :weight WHERE rowid = :id"

    cursor.execute("BEGIN TRANSACTION")
    for item in contents:
        rowid = uu.getOne(cursor, query1, {"radical": item[0]})
        if not rowid:
            cursor.execute(query2, {"radical": item[0], "weight": item[1], "score": 1})
            tqdm.write(f"Add new radical: {item[0]}")
        else:
            cursor.execute(query3, {"id": rowid, "weight": item[1]})
    cursor.execute("COMMIT TRANSACTION")

# def performImport(args):
#     if os.path.isfile(args.output):
#         os.remove(args.output)

#     # create db

#     db = sqlite3.connect(args.output)
#     cursor = db.cursor()

#     # the radical based on unihan
#     cursor.execute('''CREATE TABLE unihan (
#         `radical` CHAR(4) UNIQUE NOT NULL,
#         `ja_JP` CHAR(4) default NULL,
#         `ko_KR` CHAR(4) default NULL,
#         `zh_Hans_CN` CHAR(4) default NULL,
#         `zh_Hans_SG` CHAR(4) default NULL,
#         `zh_Hant_HK` CHAR(4) default NULL,
#         `zh_Hant_MO` CHAR(4) default NULL,
#         `zh_Hant_TW` CHAR(4) default NULL,
#         `stroke` INTEGER default 0,
#         `weight` INTEGER default 0
#     )''')

#     # user weight
#     # cursor.execute("CREATE TABLE user_weight (`unihan_id` INTEGER UNIQUE NOT NULL, weight INTEGER default 0)")

#     cursor.execute("PRAGMA synchronous = OFF")
#     cursor.execute("PRAGMA journal_mode = MEMORY")

#     importStroke(cursor)
#     importVariant(cursor)
#     importWeight(cursor)

#     db.commit()
#     cursor.execute('vacuum')
#     cursor.execute("CREATE INDEX stroke_index ON unihan (stroke)")
#     cursor.execute("CREATE INDEX weight_index ON unihan (weight)")
#     cursor.execute("CREATE INDEX hant_index ON unihan (zh_Hant_TW)")
#     cursor.execute("CREATE INDEX hans_index ON unihan (zh_Hans_CN)")
#     # cursor.execute("CREATE INDEX user_index ON user_weight (unihan_id)")
#     db.close()

# https://www.unicode.org/reports/tr38/#kCompatibilityVariant
class Char:
    def __init__(self, node):
        self.cp = node.get('cp')
        self.text = chr(int(self.cp, 16))
        # kAlternateTotalStrokes
        # kFrequency: [1-5]
        # A rough frequency measurement for the character based on analysis of traditional Chinese USENET postings; characters with a kFrequency of 1 are the most common, those with a kFrequency of 2 are less common, and so on, through a kFrequency of 5.
        self.frequency = int(node.get('kFrequency') or '0')
        # kGradeLevel: [1-6], 1: easy, 6: hard
        # The primary grade in the Hong Kong school system by which a student is expected to know the character; this data is derived from 朗文初級中文詞典, Hong Kong: Longman, 2001.
        self.gradeLevel = int(node.get('kGradeLevel') or '0')
        # self.pinyin = node.get('kHanyuPinyin')
        # kMandarin: [a-z\x{300}-\x{302}\x{304}\x{308}\x{30C}]+
        self.mandarin = node.get('kMandarin')
        if self.mandarin:
            self.mandarin = uu.stripAccents(self.mandarin)
        # kPhonetic: [1-9][0-9]{0,3}[A-Dx]?[*+]?
        # self.phonetic = node.get('kPhonetic')
        # kSpecializedSemanticVariant
        # kSpoofingVariant
        # kStrange
        self.strange = node.get('kStrange')
        # kTotalStrokes
        # The total number of strokes in the character (including the radical). When there are two values, then the first is preferred for zh-Hans (CN) and the second is preferred for zh-Hant (TW). When there is only one value, it is appropriate for both.
        self.stroke = 0
        if node.get('kTotalStrokes'):
            strokes = node.get('kTotalStrokes').split()
            # preferred for zh-Hant (TW)
            self.stroke = int(strokes[-1])

        # kSimplifiedVariant: U\+[23]?[0-9A-F]{4}
        # self.simplifiedVariant = node.get('kSimplifiedVariant')
        # if self.simplifiedVariant:
        #     self.simplifiedVariant = chr(int(self.simplifiedVariant[2:], 16))

        self.simplifiedVariant = None
        if node.get('kSimplifiedVariant'):
            self.simplifiedVariant = []
            items = node.get('kSimplifiedVariant').split()
            for item in items:
                c = chr(int(item[2:], 16))
                if c == self.text:
                    continue
                self.simplifiedVariant.append(c)

        # kTraditionalVariant
        self.traditionalVariant = None
        if node.get('kTraditionalVariant'):
            self.traditionalVariant = []
            items = node.get('kTraditionalVariant').split()
            for item in items:
                c = chr(int(item[2:], 16))
                if c == self.text:
                    continue
                self.traditionalVariant.append(c)
            self.traditionalVariant.reverse()
        # self.traditionalVariant = chr(int(self.traditionalVariant[2:], 16))

        # score
        score = 0
        if not self.strange:
            score += 1
        if self.gradeLevel:
            score += 7 - self.gradeLevel
        if self.frequency:
            score += 6 - self.frequency
        if not self.traditionalVariant:
            score += 1
        self.score = score

    def __str__(self):
        return f"{self.cp} => {self.text}\tScore: {self.score}\tMandarin: {self.mandarin}\tHans: {self.simplifiedVariant}\tHant: {self.traditionalVariant}\tStroke: {self.stroke}\tS: {self.strange}\tFreq: {self.frequency}\tLevel: {self.gradeLevel}"

def parseRadical(cursor, repo, namespace):
    counter = 0

    query = "INSERT INTO `unihan` (`radical`, `pinyin`, `score`, `stroke`, `weight`) VALUES (:radical, :pinyin, :score, :stroke, :weight)"
    cursor.execute("BEGIN TRANSACTION")

    for child in tqdm(repo.findall('ucd:char', namespace), unit = 'MB', unit_scale = True, ascii = True, desc = f"Radical"):
    # for child in repo.findall('ucd:char', namespace):
        if consoleBufferSize > 0 and counter > consoleBufferSize:
            break
        counter += 1

        char = Char(child)
        params = {
            "radical": char.text,
            "pinyin": char.mandarin or None,
            "score": char.score,
            "stroke": char.stroke,
            "weight": 0,
        }
        cursor.execute(query, params)

    cursor.execute("COMMIT TRANSACTION")

def parseSimplified(cursor, repo, namespace):
    counter = 0

    query1 = "SELECT `rowid` FROM `unihan` WHERE `radical` = :radical LIMIT 1"
    query2 = "INSERT INTO `t2s` (`hant_id`, `hans_id`) VALUES (:hant_id, :hans_id)"

    cursor.execute("BEGIN TRANSACTION")

    for child in tqdm(repo.findall('ucd:char', namespace), unit = 'MB', unit_scale = True, ascii = True, desc = f"t2s"):
    # for child in repo.findall('ucd:char', namespace):
        char = Char(child)
        if not char.simplifiedVariant:
            continue

        if consoleBufferSize > 0 and counter > consoleBufferSize:
            break
        counter += 1

        hant_id = uu.getOne(cursor, query1, {"radical": char.text})
        if not hant_id:
            print("Radical not found")
            print(char)
            sys.exit()

        for c in char.simplifiedVariant:
            hans_id = uu.getOne(cursor, query1, {"radical": c})
            if not hans_id:
                print("Hans radical not found")
                print(char)
                # sys.exit()
                continue
            cursor.execute(query2, {"hant_id": hant_id, "hans_id": hans_id})
            # tqdm.write(f"[t2s]: {char.text} => {c}")

    cursor.execute("COMMIT TRANSACTION")

def parseTraditional(cursor, repo, namespace):
    counter = 0

    query1 = "SELECT `rowid` FROM `unihan` WHERE `radical` = :radical LIMIT 1"
    query2 = "INSERT INTO `s2t` (`hans_id`, `hant_id`) VALUES (:hans_id, :hant_id)"

    cursor.execute("BEGIN TRANSACTION")

    for child in tqdm(repo.findall('ucd:char', namespace), unit = 'MB', unit_scale = True, ascii = True, desc = f"s2t"):
    # for child in repo.findall('ucd:char', namespace):
        char = Char(child)
        if not char.traditionalVariant:
            continue

        if consoleBufferSize > 0 and counter > consoleBufferSize:
            break
        counter += 1

        hans_id = uu.getOne(cursor, query1, {"radical": char.text})
        if not hans_id:
            print("Radical not found")
            print(char)
            sys.exit()

        for c in char.traditionalVariant:
            hant_id = uu.getOne(cursor, query1, {"radical": c})
            if not hant_id:
                print("Hant radical not found")
                print(char)
                sys.exit()
            cursor.execute(query2, {"hant_id": hant_id, "hans_id": hans_id})

    cursor.execute("COMMIT TRANSACTION")

def importRadical(cursor, task):
    path = f"{basedir}/rawdata/Unihan/ucd.unihan.flat.xml"
    namespace = {
        'ucd': 'http://www.unicode.org/ns/2003/ucd/1.0',
    }
    root = xet.parse(path).getroot()
    repo = root.find('ucd:repertoire', namespace)

    if task == "radical":
        parseRadical(cursor, repo, namespace)
    elif task == "t2s":
        parseSimplified(cursor, repo, namespace)
    elif task == "s2t":
        parseTraditional(cursor, repo, namespace)

# def test(cursor):
#     query = '''SELECT
#         t.radical AS hant,
#         s.radical AS hans
#     FROM t2s
#         LEFT JOIN unihan AS t ON (t.rowid = t2s.hant_id)
#         LEFT JOIN unihan AS s ON (s.rowid = t2s.hans_id)'''
#     rows = cursor.execute(query)
#     print(rows)


def main():
    argParser = argparse.ArgumentParser(description='Unihan Utility')
    # argParser.add_argument('-i', '--input', help='base dir of the repo')
    argParser.add_argument('-o', '--output', default='', help='output db path')

    args = argParser.parse_args()
    # performImport(args)
    # performViewer()

    if os.path.isfile(args.output):
        os.remove(args.output)

    # create db

    db = sqlite3.connect(args.output)
    cursor = db.cursor()

    # the radical based on unihan

    cursor.execute('''CREATE TABLE unihan (
        `radical` CHAR(4) UNIQUE NOT NULL,
        `pinyin` CHAR(10) default NULL,
        `stroke` INTEGER default 0,
        `score` INTEGER default 0,
        `weight` INTEGER default 0
    )''')

    cursor.execute('''CREATE TABLE t2s (
        `hant_id` INTEGER default 0,
        `hans_id` INTEGER default 0
    )''')

    cursor.execute('''CREATE TABLE s2t (
        `hans_id` INTEGER default 0,
        `hant_id` INTEGER default 0
    )''')


    # user weight
    # cursor.execute("CREATE TABLE user_weight (`unihan_id` INTEGER UNIQUE NOT NULL, weight INTEGER default 0)")

    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA journal_mode = MEMORY")

    importRadical(cursor, "radical")
    importRadical(cursor, "t2s")
    importRadical(cursor, "s2t")
    importWeight(cursor)
    # test(cursor)

    db.commit()
    cursor.execute('vacuum')
    cursor.execute("CREATE INDEX score_index ON unihan (score)")
    cursor.execute("CREATE INDEX weight_index ON unihan (weight)")
    cursor.execute("CREATE INDEX stroke_index ON unihan (stroke)")
    cursor.execute("CREATE INDEX t2s_index ON t2s (hant_id)")
    cursor.execute("CREATE INDEX s2t_index ON s2t (hans_id)")
    # cursor.execute("CREATE INDEX user_index ON user_weight (unihan_id)")
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