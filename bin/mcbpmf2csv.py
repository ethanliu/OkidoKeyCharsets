#!/usr/bin/env python
#
# autor: Ethan Liu
#
# convert McBopomofo phrase.occ to csv

import argparse
import sys, os
import csv
import re
from tqdm import tqdm
from lib.util import trim, chunks
from lib.pinyin import PinyinQuery
from lib.util import chunks, list_flatten, list_unique
from lib.bpmf import bpmf_remove_tones, bpmf_to_pinyin

# def exam(phrase, pinyin):
#     if phrase in exam_list:
#         print(f"-> {phrase} {pinyin}")

mapping = {}

def prepareMapping(input_path):
    global mapping
    path = f"{input_path}/Data/BPMFMappings.txt"

    _mapping = {}
    filename = os.path.basename(path)
    delimiter = " "

    with open(path) as fp:
        first_line = fp.readline()
        fp.seek(0)

        if "\t" in first_line:
            delimiter = "\t"

        reader = csv.reader(fp, delimiter = delimiter)
        for chunk in chunks(reader, max = 0):
            for row in tqdm(chunk, desc = f"{filename}[]", unit = 'MB', unit_scale = True, ascii = True):
                phrase = trim(row[0] or '')
                bpmf = " ".join(row[1:])
                if not phrase or not bpmf:
                    continue

                pinyin = ""
                try:
                    pinyin = re.split(" ", trim(bpmf))
                    pinyin = " ".join([bpmf_to_pinyin(item) for item in pinyin])
                except Exception as e:
                    pinyin = ""

                # print(f"{phrase} => {bpmf} {pinyin}")
                _mapping[phrase] = pinyin

    mapping = _mapping


def parse(input_path, output_path):
    global mapping
    path = f"{input_path}/Data/phrase.occ"
    filename = os.path.basename(path)
    qm = PinyinQuery()
    contents = ""
    delimiter = " "

    with open(path) as fp:
        first_line = fp.readline()
        fp.seek(0)

        if "\t" in first_line:
            delimiter = "\t"

        reader = csv.reader(fp, delimiter = delimiter)
        for chunk in chunks(reader, max = 0):
            for row in tqdm(chunk, desc = f"{filename}[]", unit = 'MB', unit_scale = True, ascii = True):
                phrase = trim(row[0] or '')
                if not phrase:
                    continue

                weight = (row[1:2] or ('0', ''))[0]
                phrase_pinyin = mapping.get(phrase) or None

                if not phrase_pinyin:
                    phrase_pinyin = qm.find("hant", phrase)

                if phrase_pinyin == phrase or phrase_pinyin == None:
                    phrase_pinyin = ''

                contents += f"{phrase}\t{weight}\t{phrase_pinyin}\n"
                # for quick exam
                # exam(phrase, phrase_pinyin)

    qm.close()
    with open(output_path, 'w') as fp:
        fp.write(contents)
        fp.close()

def updateVersion(input_path):
    # version...
    path = f"{input_path}/McBopomofo-Info.plist"
    contents = ''
    with open(path, 'r') as fp:
        contents = fp.read()

    pattern = r"CFBundleShortVersionString</key>[\n\s]+<string>(.*)</string>"
    result = re.findall(pattern, contents, re.MULTILINE)
    version = result[0] or None

    if version:
        print(f"Patching version: {version}")
        basedir = os.path.normpath(os.path.join(os.path.dirname(__file__), os.path.pardir))
        path = f"{basedir}/lexicon/mcbopomofo.csv.txt"

        contents = ''
        with open(path, 'r') as file:
            contents = file.read()
        contents = re.sub(r'小麥注音輸入法 (.*) 版本', f"小麥注音輸入法 {version} 版本", contents)
        # print(contents)
        with open(path, 'w') as file:
            file.write(contents)

def main():
    arg_reader = argparse.ArgumentParser(description='McBopomofo tookit')
    arg_reader.add_argument('-i', '--input', help='Source dir')
    arg_reader.add_argument('-o', '--output', default='', help='Lexicon format csv file path')

    args = arg_reader.parse_args()
    # print(args, len(sys.argv))

    if not os.path.exists(args.input):
        sys.exit(f"File not found: {args.input}")

    prepareMapping(args.input)
    parse(args.input, args.output)
    updateVersion(args.input)

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
