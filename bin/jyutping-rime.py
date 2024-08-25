#!/usr/bin/env python
#
# version: 0.0.1
# autor: Ethan Liu
#
# convert McBopomofo BPMFMappings.txt to csv

import argparse
# import importlib
import sys, os
import csv
import re
# import sqlite3
# import pinyin as tp
from tqdm import tqdm
from lib.util import trim, chunks

# uu = importlib.import_module("lib.util")

def phrase2csv(input_path, output_path):
    filename = os.path.basename(input_path)
    contents = ""
    began = False

    with open(input_path) as fp:
        reader = csv.reader(fp, delimiter = '\t')
        for chunk in chunks(reader, max = 0):
            for row in tqdm(chunk, desc = f"{filename}[]", unit = 'MB', unit_scale = True, ascii = True):
                if not row:
                    # print(f"skip empty: {row}")
                    continue;

                if not began:
                    # print(f"skip info: {row}")
                    if row and row[0] == '...':
                        began = True
                    continue

                # phrase = trim(row[0] or '')
                # pinyin = trim(''.join(row[1:] or []))
                phrase = trim(row[0] or '')
                pinyin = trim(row[1] or '')
                pinyin = re.sub('[0-9\\s]?', '', pinyin)

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

        # fp.close()

    with open(output_path, 'w') as fp:
        fp.write(contents)
        fp.close()


def yaml2cin(input_path, output_path, header_path, toneless = False):
    filename = os.path.basename(output_path)
    contents = ""
    began = False
    version = ''

    with open(input_path) as fp:
        reader = csv.reader(fp, delimiter = '\t')
        for chunk in chunks(reader, max = 0):
            for row in tqdm(chunk, desc = f"{filename}[]", unit = 'MB', unit_scale = True, ascii = True):
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

                phrase = trim(row[0] or '')
                pinyin = trim(row[1] or '')
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
                    pinyin = re.sub('[0-9\\s]?', '', pinyin)

                if pinyin == phrase:
                    pinyin = ''

                contents += f"{pinyin}\t{phrase}\n"

        fp.close()

    with open(header_path, 'r') as fp:
        template = fp.read()
        template = template.replace('{{version}}', version)
        template = template.replace('{{chardef}}', contents)
        contents = template
        template = ''
        fp.close()

    # contents = header + "\n%chardef begin\n" + contents + "%chardef end\n"

    with open(output_path, 'w') as fp:
        fp.write(contents)
        fp.close()

def main():
    arg_reader = argparse.ArgumentParser(description='Convert jyutping')
    arg_reader.add_argument('-i', '--input', help='Input file path')
    arg_reader.add_argument('-o', '--output', default='', help='Output file path')
    arg_reader.add_argument('-t', '--target', choices=['tone', 'toneless', 'phrase'], help='Convert mode')
    arg_reader.add_argument('--header', help='CIN table header')

    args = arg_reader.parse_args()
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
