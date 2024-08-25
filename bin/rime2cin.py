#!/usr/bin/env python
#
# version: 0.0.1
# autor: Ethan Liu
#
# convert rime yaml to cin table

import sys, os, argparse
# import importlib
import csv
from datetime import datetime
from tqdm import tqdm
from lib.util import trim, chunks

# uu = importlib.import_module("lib.util")

def yaml2cin(input_path, output_path, header_path):
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
                    if "version:" in row[0]:
                        version = row[0].replace('version:', '').replace('"', '').replace('\'', '').strip()

                    if row and row[0] == '...':
                        began = True
                    continue

                phrase = trim(row[0] or '')
                pinyin = trim(row[1] or '')

                if pinyin == phrase:
                    pinyin = ''

                contents += f"{pinyin}\t{phrase}\n"

        # fp.close()

    with open(header_path, 'r') as fp:
        template = fp.read()
        today = datetime.now()
        template = f"# build: {today.strftime(f'%Y/%m/%d %H:%M:%S')}\n" + template
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
    arg_reader = argparse.ArgumentParser(description='Convert CIN table from Rime YAML')
    arg_reader.add_argument('-i', '--input', required = True, help='Input file path')
    arg_reader.add_argument('-o', '--output', required = True, help='Output file path')
    arg_reader.add_argument('-x', '--header', required = True, help='CIN table header')

    args = arg_reader.parse_args()
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
