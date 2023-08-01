#!/usr/bin/env python
#
# version: 0.0.1
# autor: Ethan Liu
#
# convert rime yaml to cin table

import sys, os, argparse
import importlib
import csv
from datetime import datetime
from tqdm import tqdm

uu = importlib.import_module("lib.util")

def yaml2cin(inputPath, outputPath, headerPath):
    filename = os.path.basename(outputPath)
    contents = ""
    began = False
    version = ''

    with open(inputPath) as fp:
        reader = csv.reader(fp, delimiter = '\t')
        for chunk in uu.chunks(reader, max = 0):
            for row in tqdm(chunk, desc = f"{filename}[]", unit = 'MB', unit_scale = True, ascii = True):
                if not row:
                    # print(f"skip empty: {row}")
                    continue;

                if not began:
                    # print(f"skip info: {row}")
                    if "version:" in row[0]:
                        version = row[0].replace('version:', '').replace('"', '').replace('\'', '').strip()

                    if row and row[0] == '...':
                        began = True
                    continue

                phrase = uu.trim(row[0] or '')
                pinyin = uu.trim(row[1] or '')

                if pinyin == phrase:
                    pinyin = ''

                contents += f"{pinyin}\t{phrase}\n"

        # fp.close()

    with open(headerPath, 'r') as fp:
        template = fp.read()
        today = datetime.now()
        template = f"# build: {today.strftime(f'%Y/%m/%d %H:%M:%S')}\n" + template
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
    argParser = argparse.ArgumentParser(description='Convert CIN table from Rime YAML')
    argParser.add_argument('-i', '--input', required = True, help='Input file path')
    argParser.add_argument('-o', '--output', required = True, help='Output file path')
    argParser.add_argument('-x', '--header', required = True, help='CIN table header')

    args = argParser.parse_args()
    # print(args, len(sys.argv))

    if not os.path.exists(args.input):
        sys.exit(f"File not found: {args.input}")

    if not os.path.exists(args.header):
        sys.exit(f"File not found: {args.header}")

    yaml2cin(args.input, args.output, args.header)

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
