#!/usr/bin/env python
#
# version: 0.0.1
# autor: Ethan Liu
#
# build helper for reducing Makefile hassel
#

import sys
import os.path
import pathlib
import argparse
# from natsort import natsorted
from natsort import os_sorted
#import subprocess
#import importlib

from lib.util import prompt, run

def main():
    parser = argparse.ArgumentParser(description='builder')
    parser.add_argument('-c', '--category', choices=['table', 'lexicon', 'keyboard'], nargs='?')
    parser.add_argument('-t', '--target', choices=['json', 'db'], nargs='?')
    parser.add_argument('-i', '--inputDir', help='dir', nargs='?')
    parser.add_argument('-o', '--outputDir', help='dir', nargs='?')
    # parser.add_argument('profile', nargs='?', help='Profile filename')
    # parser.add_argument('-e', '--plugin', choices=['array', 'bossy'], help='plugin')
    # parser.add_argument('-e', '--excludes', nargs='+', help='Excludes additional profile')
    # parser.add_argument('-l', '--list', action='store_true', help='List profiles')
    # parser.add_argument('-l', '--list', action=argparse.BooleanOptionalAction, help='profile list')
    # parser.add_argument('-f', '--flush', action=argparse.BooleanOptionalAction, help='flush dns')
    # parser.add_argument('-v', '--validate', action='store_true', help='validate on/off')

    # vv = None

    # print(type(vv))
    # print(type(True))
    # print(type(1))
    # print(type(0))
    # print(type(0.0))
    # print(type(123))
    # print(type(123.333))
    # print(type("dddd"))
    # _prompt = prompt("Delete all existing file? [y/N]", False)
    # _prompt = prompt("Delete all existing file? [y/N]", 1)
    # _prompt = prompt("Delete all existing file? [y/N]", False)
    # _prompt = prompt("Delete all existing file? [y/N]", 'N')
    # sys.exit()

    args = parser.parse_args()
    print('args:', args)

    # test
    # args.category = 'table'
    # args.target = 'db'
    # args.inputDir = 'table'
    # args.outputDir = 'dist/queue/table'

    match args.category:
        case 'table':
            if args.target == 'db':
                _table_db(args.inputDir, args.outputDir)
        case 'lexicon':
            if args.target == 'db':
                _lexicon_db(args.inputDir, args.outputDir)
        case 'keyboard':
            pass
        case _:
            print("No matching category")
            pass

    # if args.flush:
    #     flush()
    #     sys.exit()

    # if args.dir == None or args.dir == "":
    #     args.dir = os.path.dirname(os.path.abspath(__file__)) + "/hosts.d"

    # if os.path.exists(args.dir) == False:
    #     sys.exit("Profiles dir \"" + args.dir + "\" not found")

    # if args.list == True:
    #     list(args.dir)
    #     sys.exit(0)


    # if args.profile == None:
    #     sys.exit("Missing profile")

    # profilePath = os.path.join(args.dir, args.profile + ".conf")
    # if os.path.isfile(profilePath) == False:
    #     sys.exit(profilePath + " not found")


def _lexicon_db(inputDir: str, outputDir: str):
    if not os.path.exists(inputDir):
        print(f"[404]: {inputDir}")
    if not os.path.exists(outputDir):
        print(f"[404]: {outputDir}")

    deleteOldFile = prompt("Delete old file before build?", False)
    for path in os_sorted(list(pathlib.Path(inputDir).glob("*.csv"))):
        # filename = pathlib.Path(path).stem
        filename = pathlib.Path(path).name
        outputPath = f"{outputDir}/{filename}.db"

        if os.path.exists(outputPath):
            if deleteOldFile:
                # print(f"[X] delete {outputPath}")
                os.remove(outputPath)
            else:
                print(f"[X] {filename}")
                continue

        if filename.startswith('_'):
            continue

        cmd = f"bin/lexicon2db.py -i {path} -o {outputPath}"
        # print(f"-> cmd: {cmd}")
        run(cmd)

def _table_db(inputDir: str, outputDir: str):
    if not os.path.exists(inputDir):
        print(f"[404]: {inputDir}")
    if not os.path.exists(outputDir):
        print(f"[404]: {outputDir}")

    excludes = [
		"array-shortcode.cin",
		"array30.cin",
		"biaoyin.cin",
		"boshiamy.cin",
		"cj-ext.cin",
		"egyptian.cin",
		"jtcj.cin",
		"jyutping.cin",
		"kk.cin",
		"ov_ez.cin",
		"ov_ez75.cin",
		"ov_ezbig.cin",
		"ov_ezsmall.cin",
		"pictograph.cin",
		"stroke-stroke5.cin",
		"tcj.cin",
		# "dayi4.cin",
		"dayi3-patched.cin",
        "array-special.cin",
        "bossy.cin",
        "bpmf-ext.cin",
        "bpmf-orig.cin",
        "cj-j.cin",
        "cj-wildcard.cin",
        "ehq-symbols.cin",
        "esperanto.cin",
        "jinjin.cin",
        "jyutping-toneless.cin",
        "kks.cin",
        "klingon.cin",
        "liu.cin",
        "morse.cin",
        "NewCJ3.cin",
        "poj-holo.cin",
        "qcj.cin",
        "simplex-ext.cin",
        "telecode.cin",
        "tp_hakka_hl.cin",
        "tp_hakka_sy.cin",
        "wu.cin",
        "wubizixing.cin",
        "wus.cin",
    ]

    deleteOldFile = prompt("Delete old file before build?", False)
    for path in os_sorted(list(pathlib.Path(inputDir).glob("*.cin"))):
        # filename = pathlib.Path(path).stem
        filename = pathlib.Path(path).name
        outputPath = f"{outputDir}/{filename}.db"

        if os.path.exists(outputPath):
            if deleteOldFile:
                # print(f"[X] delete {outputPath}")
                os.remove(outputPath)
            else:
                print(f"[X] {filename}")
                continue

        if filename.startswith('_') or filename in excludes:
            continue

        cmd = f"bin/cin2db.py -i {path} -o {outputPath}"
        if filename.startswith("array30"):
            cmd = f"{cmd} -e array"
        # print(f"-> cmd: {cmd}")
        run(cmd)

    pass


if __name__ == "__main__":
    main()