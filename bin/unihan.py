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
from enum import IntEnum

uu = importlib.import_module("lib.util")

basedir = os.path.normpath(os.path.join(os.path.dirname(__file__), os.path.pardir))

# https://www.unicode.org/reports/tr38/#kCompatibilityVariant

# or ignore range? F900–FAFF，2F800–2FA1F
class Classified(IntEnum):
    Common = 1
    LessCommon = 2
    Rare = 3
    Newly = 10
    # for sorting friendly purpose, giving a large number instead of zero
    Unclassified = 99

    @staticmethod
    def fromCategory(category):
        match category:
            case 'A':
                return Classified.Common
            case 'B':
                return Classified.LessCommon
            case 'C':
                return Classified.Rare
            case 'N':
                return Classified.Newly
            case _:
                return Classified.Unclassified


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
        # self.fenn = node.get('kFenn')
        self.tsource = node.get('kIRG_TSource')
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
        if self.gradeLevel:
            score += 7 - self.gradeLevel
        if self.frequency:
            score += 6 - self.frequency
        if self.mandarin:
            score += 1
        if not self.strange:
            score += 1
        if not self.traditionalVariant:
            score += 1
        self.score = score

        self.classified = Classified.Unclassified
        # if self.traditionalVariant:
        #     self.classified = Classified.Simplified
        # if self.strange:
        #     self.classified = 1
        # elif self.traditionalVariant:
        #     if len(self.traditionalVariant) >= 2:
        #         self.classified = 2
        #     else:
        #         self.classified = 3

    def __str__(self):
        # \tStroke: {self.stroke}\tFreq: {self.frequency}\tLevel: {self.gradeLevel}
        return f"{self.cp} => {self.text}\tTS: {self.tsource}\tStrange: {self.strange}\tScore: {self.score}\tMandarin: {self.mandarin}\tHans: {self.simplifiedVariant}\tHant: {self.traditionalVariant}"

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
            cursor.execute(query2, {"radical": item[0], "weight": item[1], "score": 1, "classified": Classified.Unclassified})
            tqdm.write(f"Add new radical: {item[0]}")
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

def parseRadical(cursor, repo, namespace):
    query = "INSERT INTO `radical` (`radical`, `pinyin`, `classified`, `score`, `stroke`, `weight`) VALUES (:radical, :pinyin, :classified, :score, :stroke, :weight)"

    cursor.execute("BEGIN TRANSACTION")

    for chunk in uu.chunks(repo.findall('ucd:char', namespace), max = 0):
        for child in tqdm(chunk, desc = f"Unihan[Radical]", unit = 'MB', unit_scale = True, ascii = True):
        # for child in tqdm(repo.findall('ucd:char', namespace), unit = 'MB', unit_scale = True, ascii = True, desc = f"Radical"):
        # for child in repo.findall('ucd:char', namespace):
            char = Char(child)

            params = {
                "radical": char.text,
                "pinyin": char.mandarin or None,
                "classified": char.classified,
                "score": char.score,
                "stroke": char.stroke,
                "weight": 0,
            }
            cursor.execute(query, params)

        cursor.execute("COMMIT TRANSACTION")

def parseSimplified(cursor, repo, namespace):
    query1 = "SELECT `rowid` FROM `radical` WHERE `radical` = :radical LIMIT 1"
    query2 = "INSERT INTO `t2s` (`hant_id`, `hans_id`) VALUES (:hant_id, :hans_id)"

    cursor.execute("BEGIN TRANSACTION")

    for chunk in uu.chunks(repo.findall('ucd:char', namespace), max = 0):
        for child in tqdm(chunk, desc = f"Unihan[SC]", unit = 'MB', unit_scale = True, ascii = True):
        # for child in tqdm(repo.findall('ucd:char', namespace), unit = 'MB', unit_scale = True, ascii = True, desc = f"t2s"):
        # for child in repo.findall('ucd:char', namespace):
            char = Char(child)
            if not char.simplifiedVariant:
                continue

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
    query1 = "SELECT `rowid` FROM `radical` WHERE `radical` = :radical LIMIT 1"
    query2 = "INSERT INTO `s2t` (`hans_id`, `hant_id`) VALUES (:hans_id, :hant_id)"

    cursor.execute("BEGIN TRANSACTION")

    for chunk in uu.chunks(repo.findall('ucd:char', namespace), max = 0):
        for child in tqdm(chunk, desc = f"Unihan[TC]", unit = 'MB', unit_scale = True, ascii = True):
        # for child in tqdm(repo.findall('ucd:char', namespace), unit = 'MB', unit_scale = True, ascii = True, desc = f"s2t"):
        # for child in repo.findall('ucd:char', namespace):
            char = Char(child)

            if not char.traditionalVariant:
                continue

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

    cursor.execute('''CREATE TABLE `radical` (
        `radical` CHAR(4) UNIQUE NOT NULL,
        `pinyin` CHAR(10) default NULL,
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

    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA journal_mode = MEMORY")

    importRadical(cursor, "radical")
    importRadical(cursor, "t2s")
    importRadical(cursor, "s2t")
    importClassified(cursor)
    importWeight(cursor)
    # test(cursor)

    db.commit()
    cursor.execute('vacuum')
    cursor.execute("CREATE INDEX `score_index` ON `radical` (score)")
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