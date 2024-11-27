#!/usr/bin/env python
#
# version: 0.0.1
# autor: Ethan Liu
#
# ref:
# https://language.moe.gov.tw/001/Upload/Files/site_content/M0001/respub/index.html
#

import argparse
import sys, os
import csv
import re
import glob
from tqdm import tqdm
from lib.util import chunks, list_flatten, list_unique, trim
from lib.bpmf import bpmf_remove_tones, bpmf_to_pinyin
from lib.pinyin import PinyinQuery
from lib.moe_spider import run_spider

# import codecs


_ZHUYIN_PRONOUNCE_PATTERN = r"[（\(][變|一|ㄧ|二|三|四|五|六|語音|讀音|又音|\d]+[）\)]|<br>"
_SPACE_PATTERN = r"[\u3000|\s|，|；]+"

_INCORRECT_CHARACTER_MAPPING = {
    "一": "ㄧ",
}

_cache_pattern = '|'.join(map(re.escape, _INCORRECT_CHARACTER_MAPPING.keys()))

def replace_all(match):
    return _INCORRECT_CHARACTER_MAPPING[match.group(0)]

# phrase only use for debug
def moe_fixes(bpmf, phrase):
    global _cache_pattern
    # result = re.sub('|'.join(map(re.escape, _INCORRECT_CHARACTER_MAPPING.keys())), lambda m: _INCORRECT_CHARACTER_MAPPING[m.group()], bpmf)
    result = re.sub(_cache_pattern, replace_all, bpmf)
    if result != bpmf:
        print(f"[moe-fixed] {phrase} {bpmf} => {result}")
    return result

def parse2(input_path, output_path):
    filename = os.path.basename(input_path)
    # [A-Z][a-z][0-9] etc?
    # pattern = f"[，。「」“”『』）【】\"\',.]+"
    skipHeader = True
    contents = ""
    qm = PinyinQuery()

    with open(input_path) as fp:
        reader = csv.reader(fp, delimiter = ',')
        for chunk in chunks(reader, max = 0):
            for row in tqdm(chunk, desc = f"{filename}[]", unit = 'MB', unit_scale = True, ascii = True):
                if not row[0]:
                    continue

                if skipHeader:
                    skipHeader = False
                    continue

                phrase = row[0].strip()
                if len(phrase) < 2 or ".gif" in phrase or ".png" in phrase or phrase.startswith("_x"):
                    continue

                # _phrase = re.sub(pattern, "", phrase)
                # pinyin = tp.get(_phrase, format = "strip", delimiter = "")

                # format fixes
                zhuyin = moe_fixes(row[1], phrase)
                zhuyin = re.sub(_SPACE_PATTERN, " ", zhuyin)
                zhuyin = re.split(_ZHUYIN_PRONOUNCE_PATTERN, zhuyin)
                zhuyin = list_unique(zhuyin)

                shortcuts = []

                if not zhuyin:
                    pinyin = qm.find("hant", phrase)
                    if pinyin:
                        shortcuts.append(pinyin)
                else:
                    try:
                        for item in zhuyin:
                            pinyin = re.split(" ", trim(item))
                            pinyin = " ".join([bpmf_to_pinyin(item) for item in pinyin])
                            shortcuts.append(pinyin)
                    except Exception as e:
                        print(f"Error occurred: {e}")
                        print(f"origin: {row}")
                        shortcuts = []

                shortcuts = list_unique(shortcuts)
                for shortcut in shortcuts:
                    contents += f"{phrase}\t0\t{shortcut}\n"

    qm.close()
    with open(output_path, 'w') as fp:
        fp.write(contents)

# remove old versions
def archive(dir: str, prefix: str):
    paths = glob.glob(f"{dir}/{prefix}_*")
    sorted_paths = sorted(paths, key=os.path.getmtime)
    sorted_paths.pop()
    # print(sorted_paths)
    result = False
    if len(sorted_paths) > 1:
        result = True
    for path in sorted_paths:
        # print(f"Delete {path}")
        os.remove(path)
    return result


def main():
    arg_reader = argparse.ArgumentParser(description='Convert to lexicon-CSV-format from the original excel/csv format')
    # argParser.add_argument('-c', '--category', choices=['concised', 'idoms', 'revised'], help='Lexicon category')
    arg_reader.add_argument('-i', '--input', help='Original csv file path')
    arg_reader.add_argument('-o', '--output', default='', help='Lexicon format csv file path')
    arg_reader.add_argument('-d', '--download', action=argparse.BooleanOptionalAction, help='download')

    args = arg_reader.parse_args()
    # print(args, len(sys.argv))

    if args.download:
        if not args.output:
            sys.exit("Missing output dir")
        run_spider(args.output)
        archive(args.output, "dict_concised")
        archive(args.output, "dict_idioms")
        archive(args.output, "dict_revised")
        # archive(args.output, "dict_mini")
    else:
        if not os.path.exists(args.input):
            sys.exit(f"File not found: {args.input}")
        # codecs.register_error('asciify', asciify)
        parse2(args.input, args.output)

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
