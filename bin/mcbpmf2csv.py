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
# import sqlite3
# import multiprocessing
import pinyin as tp
from tqdm import tqdm

uu = importlib.import_module("lib.util")

# _dir_ = uu.dir(__file__)
consoleBufferSize = -1000
# workers = 2 * multiprocessing.cpu_count()
# print(f"num of workers: \(workers)")

def parse(inputPath, outputPath):
    filename = os.path.basename(inputPath)
    contents = ""
    # _dir_ = uu.dir(__file__)
    # pool = multiprocessing.Pool(workers)

    with open(inputPath) as fp:
        reader = csv.reader(fp, delimiter = ' ')
        # for row in reader:
        # for row in tqdm(reader, unit = 'MB', unit_scale = True, ascii = True, desc = f"Convert {filename}"):
        for rows in uu.chunks(reader, 100000):

            for row in tqdm(rows, unit = 'MB', unit_scale = True, ascii = True, desc = f"{filename} Chunk[]"):
                if consoleBufferSize > 0 and len(contents) > consoleBufferSize:
                    break


                phrase = uu.trim(row[0] or '')
                # weight = row[1] or 0
                weight = 0
                # pinyin = ''
                # pinyin = translate(phrase)
                pinyin = tp.get(phrase, format = "strip", delimiter = "")

                if pinyin == phrase:
                    pinyin = ''

                contents += f"{phrase}\t{weight}\t{pinyin}\n"

        fp.close()

    with open(outputPath, 'w') as fp:
        fp.write(contents)
        fp.close()

def main():
    argParser = argparse.ArgumentParser(description='Convert to lexicon-CSV-format from the McBopomofo BPMFMappings.txt')
    argParser.add_argument('-i', '--input', help='Original csv file path')
    argParser.add_argument('-o', '--output', default='', help='Lexicon format csv file path')

    args = argParser.parse_args()
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
