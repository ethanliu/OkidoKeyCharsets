#!/usr/bin/env python
#
# autor: Ethan Liu
#
# convert McBopomofo phrase.occ to csv

import argparse
import sys, os
import csv
from tqdm import tqdm
from lib.util import trim, chunks
from lib.pinyin import PinyinQuery

# def exam(phrase, pinyin):
#     if phrase in exam_list:
#         print(f"-> {phrase} {pinyin}")

def parse(input_path, output_path):

    qm = PinyinQuery()

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
                # pinyin = tp.get(phrase, format = "strip", delimiter = "")
                # phrase_pinyin = "".join(list_flatten(lazy_pinyin(phrase, strict=False, errors='ignore', style=Style.NORMAL)))
                # phrase_pinyin = "".join(list_flatten(pinyin(phrase, strict=False, errors='ignore', style=Style.NORMAL)))
                phrase_pinyin = qm.find(phrase)

                if phrase_pinyin == phrase or phrase_pinyin == None:
                    phrase_pinyin = ''

                contents += f"{phrase}\t{weight}\t{phrase_pinyin}\n"
                # for quick exam
                # exam(phrase, phrase_pinyin)

    qm.close()
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
