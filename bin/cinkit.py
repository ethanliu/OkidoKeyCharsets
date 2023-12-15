#!/usr/bin/env python
#
# version: 0.0.0
# autor: Ethan Liu
#
# description...
#

import sys
import os.path
import argparse
from lib.cintable import CinTable, CinTableParseLevel
from tqdm import tqdm

blocks = {}

blocks['x1'] = [
    {"start": 0x3300, "stop": 0x33FF, "name": "CJK Compatibility", "name_zh": "中日韓相容字元"},
    {"start": 0x4E00, "stop": 0x9FFF, "name": "CJK Unified Ideographs", "name_zh": "中日韓統一表意文字 (基本區)"},
    {"start": 0xF900, "stop": 0xFAFF, "name": "CJK Compatibility Ideographs", "name_zh": "中日韓相容表意文字"},
    {"start": 0xFE30, "stop": 0xFE4F, "name": "CJK Compatibility Forms", "name_zh": "中日韓相容形式"},
]

blocks['x2'] = [
    {"start": 0x2E80, "stop": 0x2EFF, "name": "CJK Radicals Supplement", "name_zh": "中日韓漢字部首補充"},
    {"start": 0x3000, "stop": 0x303F, "name": "CJK Symbols and Punctuation", "name_zh": "中日韓符號和標點"},
    {"start": 0x31C0, "stop": 0x31EF, "name": "CJK Strokes", "name_zh": "中日韓筆畫"},
    {"start": 0x3200, "stop": 0x32FF, "name": "Enclosed CJK Letters and Months", "name_zh": "中日韓圍繞字元及月份"},
]

blocks["a"] = [{"start": 0x3400, "stop": 0x4DBF, "name": "CJK Unified Ideographs Extension A", "name_zh": "中日韓統一表意文字擴充區 A"}]
blocks["b"] = [{"start": 0x20000, "stop": 0x2A6DF, "name": "CJK Unified Ideographs Extension B", "name_zh": "中日韓統一表意文字擴充區 B"}]
blocks["c"] = [{"start": 0x2A700, "stop": 0x2B73F, "name": "CJK Unified Ideographs Extension C", "name_zh": "中日韓統一表意文字擴充區 C"}]
blocks["d"] = [{"start": 0x2B740, "stop": 0x2B81F, "name": "CJK Unified Ideographs Extension D", "name_zh": "中日韓統一表意文字擴充區 D"}]
blocks["e"] = [{"start": 0x2B820, "stop": 0x2CEAF, "name": "CJK Unified Ideographs Extension E", "name_zh": "中日韓統一表意文字擴充區 E"}]
blocks["f"] = [{"start": 0x2CEB0, "stop": 0x2EBEF, "name": "CJK Unified Ideographs Extension F", "name_zh": "中日韓統一表意文字擴充區 F"}]
blocks["g"] = [{"start": 0x30000, "stop": 0x3134F, "name": "CJK Unified Ideographs Extension G", "name_zh": "中日韓統一表意文字擴充區 G"}]
blocks["h"] = [{"start": 0x31350, "stop": 0x323AF, "name": "CJK Unified Ideographs Extension H", "name_zh": "中日韓統一表意文字擴充區 H"}]
blocks["i"] = [{"start": 0x2EBF0, "stop": 0x2EE5F, "name": "CJK Unified Ideographs Extension I", "name_zh": "中日韓統一表意文字擴充區 I"}]
blocks["x"] = [{"start": 0x2F800, "stop": 0x2FA1F, "name": "CJK Compatibility Ideographs Supplement", "name_zh": "中日韓相容表意文字補充區"}]

def performMerge(args):
    mainCin = CinTable(args.path, level = CinTableParseLevel.Full)

    for path in args.merge:
        filename = os.path.basename(path)
        ref = CinTable(path, level = CinTableParseLevel.Full)
        for item in tqdm(ref.chardef, ascii=True, unit_scale=True, desc=f"{filename}"):
            if item in mainCin.chardef:
                continue
            mainCin.chardef.append(item)

    mainCin.validate()

    #  dump chardef
    for item in mainCin.chardef:
        print(f"{item[0]}\t{item[1]}")


def performDiff(args):
    cinList = []
    blockList = []

    cin = CinTable(args.path, level = CinTableParseLevel.Full)
    for item in cin.chardef:
        cinList.append(item[1])
    cinList = list(dict.fromkeys(cinList))

    # block
    for agb in args.block:
        for block in blocks[agb]:
            lower = block["start"]
            upper = block["stop"] + 1
            for v in tqdm(range(lower, upper), ascii=True, unit_scale=True, desc=f"{block['name']}"):
                try:
                    glyph = chr(v).encode('utf-16','surrogatepass').decode('utf-16')
                    if glyph in cinList:
                        continue
                    blockList.append(glyph)
                except UnicodeDecodeError as err:
                    pass
                except UnicodeEncodeError as err:
                    pass

    blockList = list(dict.fromkeys(blockList))
    newList = [x for x in blockList if x not in cinList]

    # dump
    # print(newList)
    newList = list(dict.fromkeys(newList))
    for item in newList:
        print(f"#\t{item}")


def main():
    argParser = argparse.ArgumentParser(description='CIN tookit')
    argParser.add_argument('-m', '--merge', nargs = '+', help='CIN table paths for merging to main CIN table')
    argParser.add_argument('-b', '--block', nargs = '+', choices=['x1', 'x2', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'x'], help='CJK Unified Ideographs Extension Section')
    argParser.add_argument('path', help='The main CIN table path')

    args = argParser.parse_args()
    # print(args, len(sys.argv))

    if args.merge:
        performMerge(args)
    elif args.block:
        performDiff(args)

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

if __name__ == "__main__":
    main()
