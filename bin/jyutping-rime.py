#!/usr/bin/env python
#
# version: 0.0.1
# autor: Ethan Liu
#
# convert McBopomofo BPMFMappings.txt to csv

import argparse
import importlib
import sys, os
import csv
import re
# import sqlite3
# import pinyin as tp
from tqdm import tqdm

uu = importlib.import_module("lib.util")

consoleBufferSize = -1000

def phrase2csv(inputPath, outputPath):
    filename = os.path.basename(inputPath)
    contents = ""
    began = False

    with open(inputPath) as fp:
        reader = csv.reader(fp, delimiter = '\t')
        for rows in uu.chunks(reader, 100000):
            for row in tqdm(rows, unit = 'MB', unit_scale = True, ascii = True, desc = f"{filename} Chunk[]"):
                if not row:
                    # print(f"skip empty: {row}")
                    continue;

                if not began:
                    # print(f"skip info: {row}")
                    if row and row[0] == '...':
                        began = True
                    continue

                if consoleBufferSize > 0 and len(contents) > consoleBufferSize:
                    break

                # phrase = uu.trim(row[0] or '')
                # pinyin = uu.trim(''.join(row[1:] or []))
                phrase = uu.trim(row[0] or '')
                pinyin = uu.trim(row[1] or '')
                pinyin = re.sub('[0-9\s]?', '', pinyin)

                weight = '0'

                try:
                    weight = row[2]
                except IndexError:
                    weight = '0'

                if weight == '0%':
                    weight = 10
                elif '%' in weight:
                    weight = int(weight.replace('%', '')) * 100
                else:
                    weight = int(weight)

                # print(f"row: {row[1:]}")
                # print(f"row: {phrase} | {pinyin}")

                if pinyin == phrase:
                    pinyin = ''

                contents += f"{phrase}\t{weight}\t{pinyin}\n"

        fp.close()

    with open(outputPath, 'w') as fp:
        fp.write(contents)
        fp.close()


def yaml2cin(inputPath, outputPath, headerPath, toneless = False):
    filename = os.path.basename(outputPath)
    contents = ""
    began = False
    version = ''

    with open(inputPath) as fp:
        reader = csv.reader(fp, delimiter = '\t')
        for rows in uu.chunks(reader, 100000):
            for row in tqdm(rows, unit = 'MB', unit_scale = True, ascii = True, desc = f"{filename} Chunk[]"):
                if not row:
                    # print(f"skip empty: {row}")
                    continue;

                if not began:
                    # print(f"skip info: {row}")
                    # TODO: using with RE
                    if "version:" in row[0]:
                        version = row[0].replace('version:', '').replace('"', '').replace('\'', '').strip()

                    if row and row[0] == '...':
                        began = True
                    continue

                if consoleBufferSize > 0 and len(contents) > consoleBufferSize:
                    break

                phrase = uu.trim(row[0] or '')
                pinyin = uu.trim(row[1] or '')
                # weight = '0'

                # try:
                #     weight = row[2]
                # except IndexError:
                #     weight = '0'

                # if weight == '0%':
                #     weight = 10
                # elif '%' in weight:
                #     weight = int(weight.replace('%', '')) * 100
                # else:
                #     weight = int(weight)

                # print(f"row: {row}, weight: {weight}")

                if toneless:
                    pinyin = re.sub('[0-9\s]?', '', pinyin)

                if pinyin == phrase:
                    pinyin = ''

                contents += f"{pinyin}\t{phrase}\n"

        fp.close()

    with open(headerPath, 'r') as fp:
        template = fp.read()
        template = template.replace('{{version}}', version)
        template = template.replace('{{chardef}}', contents)
        contents = template
        template = ''
        fp.close()

    # contents = header + "\n%chardef begin\n" + contents + "%chardef end\n"

    with open(outputPath, 'w') as fp:
        fp.write(contents)
        fp.close()

def main():
    argParser = argparse.ArgumentParser(description='Convert jyutping')
    argParser.add_argument('-i', '--input', help='Input file path')
    argParser.add_argument('-o', '--output', default='', help='Output file path')
    argParser.add_argument('-t', '--target', choices=['tone', 'toneless', 'phrase'], help='Convert mode')
    argParser.add_argument('--header', help='CIN table header')

    args = argParser.parse_args()
    # print(args, len(sys.argv))

    if not os.path.exists(args.input):
        sys.exit(f"File not found: {args.input}")

    if args.target == 'phrase':
        phrase2csv(args.input, args.output)
    else:
        if not os.path.exists(args.header):
            sys.exit(f"File not found: {args.header}")
        if args.target == 'tone':
            yaml2cin(args.input, args.output, args.header, False)
        elif args.target == 'toneless':
            yaml2cin(args.input, args.output, args.header, True)

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
