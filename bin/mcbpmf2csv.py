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
# import sqlite3
# import multiprocessing
import pinyin as tp
from tqdm import tqdm
from lib.util import trim, chunks

# uu = importlib.import_module("lib.util")

# _dir_ = dir(__file__)
# workers = 2 * multiprocessing.cpu_count()
# print(f"num of workers: \(workers)")

def parse(input_path, output_path):
    filename = os.path.basename(input_path)
    contents = ""
    delimiter = " "
    # _dir_ = dir(__file__)
    # pool = multiprocessing.Pool(workers)
    with open(input_path) as fp:
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
                # pinyin = translate(phrase)
                pinyin = tp.get(phrase, format = "strip", delimiter = "")

                if pinyin == phrase:
                    pinyin = ''

                contents += f"{phrase}\t{weight}\t{pinyin}\n"

    with open(output_path, 'w') as fp:
        fp.write(contents)
        fp.close()

def main():
    arg_reader = argparse.ArgumentParser(description='McBopomofo tookit')
    arg_reader.add_argument('-i', '--input', help='Original csv file path')
    arg_reader.add_argument('-o', '--output', default='', help='Lexicon format csv file path')

    args = arg_reader.parse_args()
    # print(args, len(sys.argv))

    if not os.path.exists(args.input):
        sys.exit(f"File not found: {args.input}")

    parse(args.input, args.output)

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
