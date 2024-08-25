#!/usr/bin/env python
#
# version: 0.0.1
# autor: Ethan Liu
#
# convert jieba dict.txt to csv

import argparse
import importlib
import sys, os
import csv
# import sqlite3
# import multiprocessing
from tqdm import tqdm
# import pinyin as tp
from pypinyin import lazy_pinyin, Style
from bin.lib.util import list_flatten
from lib.util import dir, exec, trim, chunks

# uu = importlib.import_module("lib.util")

_dir_ = dir(__file__)

# workers = 2 * multiprocessing.cpu_count()
# print(f"num of workers: \(workers)")

# def translate(str):
#     if not str:
#         return ''

#     result = exec([f"{_dir_}/CharTransformer", '-pinyin', str])
#     result = ''.join(result.decode()).replace(' ', '').strip()
#     return result

def parse(input_path, output_path):
    filename = os.path.basename(input_path)
    contents = ""
    # _dir_ = dir(__file__)
    # pool = multiprocessing.Pool(workers)

    with open(input_path) as fp:
        reader = csv.reader(fp, delimiter = ' ')
        for chunk in chunks(reader, max = 0):
            for row in tqdm(chunk, desc = f"{filename}[]", unit = 'MB', unit_scale = True, ascii = True):
                phrase = trim(row[0] or '')
                weight = row[1] or 0
                pinyin = ''

                # pinyin = translate(phrase)
                # pinyin = tp.get(phrase, format = "strip", delimiter = "")
                pinyin = "".join(list_flatten(lazy_pinyin(phrase, strict=False, errors='ignore', style=Style.NORMAL)))

                if pinyin == phrase or pinyin == '':
                    continue
                    # pinyin = ''

                contents += f"{phrase}\t{weight}\t{pinyin}\n"

        fp.close()
        # tqdm.write(contents)

    with open(output_path, 'w') as fp:
        fp.write(contents)
        fp.close()

def main():
    arg_reader = argparse.ArgumentParser(description='Convert to lexicon-CSV-format from the Jeiba dict.txt')
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
