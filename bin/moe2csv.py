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
from tqdm import tqdm
from lib.util import chunks, list_flatten, list_unique
from lib.bpmf import bpmf_remove_tones, bpmf_to_pinyin
# import codecs
# import pinyin as tp
from pypinyin import lazy_pinyin, Style

_ZHUYIN_PRONOUNCE_PATTERN = r"[（\(][變|一|二|三|四|五|六|語音|讀音|又音|\d]+[）\)]|<br>"
_SPACE_PATTERN = r"[\u3000|\s|，|；]+"

def parse2(input_path, output_path):
    filename = os.path.basename(input_path)
    # [A-Z][a-z][0-9] etc?
    # pattern = f"[，。「」“”『』）【】\"\',.]+"
    skipHeader = True
    contents = ""

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

                shortcuts = []
                try:
                    shortcuts = re.split(_ZHUYIN_PRONOUNCE_PATTERN, bpmf_remove_tones(row[1]))
                    shortcuts = [re.split(_SPACE_PATTERN, item.strip()) for item in shortcuts]
                    shortcuts = list_unique([bpmf_to_pinyin(item) for item in shortcuts])
                except IndexError:
                    shortcuts = []

                if not shortcuts:
                    shortcuts.append("".join(list_flatten(lazy_pinyin(phrase, strict=False, errors='ignore', style=Style.NORMAL))))

                for shortcut in shortcuts:
                    contents += f"{phrase}\t0\t{shortcut}\n"

                # print(contents)
                # sys.exit(0)

    with open(output_path, 'w') as fp:
        fp.write(contents)


def main():
    arg_reader = argparse.ArgumentParser(description='Convert to lexicon-CSV-format from the original excel/csv format')
    # argParser.add_argument('-c', '--category', choices=['concised', 'idoms', 'revised'], help='Lexicon category')
    # argParser.add_argument('-d', '--download', action='store_true', help='download...')
    arg_reader.add_argument('-i', '--input', help='Original csv file path')
    arg_reader.add_argument('-o', '--output', default='', help='Lexicon format csv file path')

    args = arg_reader.parse_args()
    # print(args, len(sys.argv))

    # if args.download:
    #     download()
    #     sys.exit("download fin.")

    if not os.path.exists(args.input):
        sys.exit(f"File not found: {args.input}")

    # codecs.register_error('asciify', asciify)
    parse2(args.input, args.output)

    # if args.category == "concised":
    #     parseConcised(args.path, args.output)
    # elif args.category == "idoms":
    #     parseConcised(args.path, args.output)
    # elif args.category == "revised":
    #     parseConcised(args.path, args.output)

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
