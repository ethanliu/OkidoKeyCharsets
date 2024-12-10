#!/usr/bin/env python
#
# autor: Ethan Liu
#
# cc-cedict helper
#

import os
import sys
import re
import argparse
from tqdm import tqdm
from lib.util import dir, chunks, trim, strip_accents, write_file, whitespace
from lib.cedict_spider import run_spider

# BASE_DIR = dir(__file__ + "/../")
# SOURCE_PATH = f"{BASE_DIR}/rawdata/cedict/cedict_ts.u8"

def parse(path):
    pattern = r'(.*) (.*) \[(.*)\] \/(.*)\/'
    rows = [];
    with open(path) as fp:
        for chunk in chunks(fp, max = 0):
            for row in tqdm(chunk, desc = "CEDICT", unit = 'MB', unit_scale = True, ascii = True):
                row = trim(row, "#")
                if row == "":
                    continue
                items = [trim(x) for x in re.split(pattern, row) if x]
                hant = whitespace(items[0])
                hans = whitespace(items[1])

                pinyin = (items[2] or '').lower()
                # ü (u:) -> u
                pinyin = pinyin.replace("u:", "u")
                # hyphen, syllable
                pinyin = pinyin.replace(" - ", " ")
                # Commas are sometimes used in Chinese proverbs
                pinyin = pinyin.replace(" , ", " ")
                # Middle dots are often used for separating western names:
                pinyin = pinyin.replace("・", " ")
                # pinyin2 = strip_accents(pinyin, True)

                glosses = [trim(x) for x in re.split(r';', items[3]) if x]
                # print(f"=> {row}")
                item = {
                    "hant": hant,
                    "hans": hans,
                    "pinyin": pinyin,
                    # "pinyin2": pinyin2,
                    "glosses": ";".join(glosses),
                }
                rows.append(item)
    return rows

def export_csv(rows, locale, path):
    contents = ""
    for row in rows:
        contents += f"{row[locale]}\t0\t{row['pinyin']}\n";
    write_file(path, contents)

def main():
    arg_reader = argparse.ArgumentParser(description='')
    arg_reader.add_argument('-i', '--input', help='cedict_ts.u8 path')
    arg_reader.add_argument('-o', '--output', default='', help='output dir')
    arg_reader.add_argument('-d', '--download', action=argparse.BooleanOptionalAction, help='download')

    args = arg_reader.parse_args()
    # print(args, len(sys.argv))

    if args.download:
        run_spider(args.output)
    else:
        rows = parse(args.input)
        export_csv(rows, "hant", f"{args.output}/cedict-hant.csv")
        export_csv(rows, "hans", f"{args.output}/cedict-hans.csv")



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
