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
# import codecs
import pinyin as tp
from tqdm import tqdm
from lib.util import chunks

def parse2(inputPath, outputPath):
    filename = os.path.basename(inputPath)
    # [A-Z][a-z][0-9] etc?
    pattern = f"[，。「」“”『』）【】\"\',.]+"
    skipHeader = True
    contents = ""

    with open(inputPath) as fp:
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

                _phrase = re.sub(pattern, "", phrase)
                pinyin = tp.get(_phrase, format = "strip", delimiter = "")
                contents += f"{phrase}\t0\t{pinyin}\n"

    with open(outputPath, 'w') as fp:
        fp.write(contents)


def main():
    argParser = argparse.ArgumentParser(description='Convert to lexicon-CSV-format from the original excel/csv format')
    # argParser.add_argument('-c', '--category', choices=['concised', 'idoms', 'revised'], help='Lexicon category')
    argParser.add_argument('-i', '--input', help='Original csv file path')
    argParser.add_argument('-o', '--output', default='', help='Lexicon format csv file path')

    args = argParser.parse_args()
    # print(args, len(sys.argv))

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
