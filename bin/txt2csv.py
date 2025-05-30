#!/usr/bin/env python
#
# version: 0.0.1
# autor: Ethan Liu
#
# Lexicon CSV
#

import sys, os, argparse
import importlib
import csv
from datetime import datetime
from tqdm import tqdm

uu = importlib.import_module("lib.util")

def txt2csv(inputPath, outputPath, column, delimiter):
    filename = os.path.basename(outputPath)
    contents = ""

    with open(inputPath) as fp:
        reader = csv.reader(fp, delimiter = delimiter)
        for chunk in uu.chunks(reader, max = 0):
            for row in tqdm(chunk, desc = f"{filename}[]", unit = 'MB', unit_scale = True, ascii = True):
                if not row:
                    # print(f"skip empty: {row}")
                    continue;

                phrase = ''
                weight = 0
                pinyin = ''

                # 3, 1, 0
                for index, i in enumerate(column):
                    if (len(row) < 2):
                        continue;
                    match i:
                        case 1:
                            # tqdm.write(f"Mapping phrase from index {index}")
                            phrase = uu.trim(row[index])
                        case 2:
                            # tqdm.write(f"Mapping weight from index {index}")
                            weight = int(row[index])
                        case 3:
                            # tqdm.write(f"Mapping pinyin from index {index}")
                            pinyin = uu.trim(row[index])

                if pinyin == phrase:
                    pinyin = ''

                contents += f"{phrase}\t{weight}\t{pinyin}\n"

        # fp.close()

    with open(outputPath, 'w') as fp:
        fp.write(contents)
        fp.close()

def main():
    argParser = argparse.ArgumentParser(description='Convert Lexicon CSV from other CSV or text file')
    argParser.add_argument('-i', '--input', required = True, help='Input file path')
    argParser.add_argument('-o', '--output', required = True, help='Output file path')

    argParser.add_argument('-d', '--delimiter', default = '\t', help='Delimiting character of the input CSV file')
    # argParser.add_argument('-t', '--tab', help='Specify that the input CSV file is delimited with tabs. Overrides "-d"')
    # argParser.add_argument('-q', '--quotechar', help='Character used to quote strings in the input CSV file')

    argParser.add_argument('-c', '--column', required = True, type = int, nargs = 3, help='column indices...')

    args = argParser.parse_args()
    # print(args, len(sys.argv))

    if not os.path.exists(args.input):
        sys.exit(f"File not found: {args.input}")

    txt2csv(args.input, args.output, args.column, args.delimiter)

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
