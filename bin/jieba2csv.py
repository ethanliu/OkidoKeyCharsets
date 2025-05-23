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
from tqdm import tqdm
from lib.util import dir, exec, trim, chunks, whitespace
from lib.pinyin import PinyinQuery

# uu = importlib.import_module("lib.util")

# _dir_ = dir(__file__)

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

    qm = PinyinQuery()

    with open(input_path) as fp:
        reader = csv.reader(fp, delimiter = ' ')
        for chunk in chunks(reader, max = 0):
            for row in tqdm(chunk, desc = f"{filename}[]", unit = 'MB', unit_scale = True, ascii = True):
                phrase = whitespace(row[0] or '')
                weight = row[1] or 0
                pinyin = qm.find("hans", phrase)

                if pinyin == phrase or pinyin == '' or pinyin == None:
                    continue
                    # pinyin = ''

                contents += f"{phrase}\t{weight}\t{pinyin}\n"

        fp.close()
        # tqdm.write(contents)

    qm.close()
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
