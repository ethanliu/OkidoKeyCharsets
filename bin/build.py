#!/usr/bin/env python
#
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

from lib.util import prompt, run, parent_dir

BASE_DIR = parent_dir(__file__, 1)
RUN = f"{BASE_DIR}/bin/run.sh"

def main():
    parser = argparse.ArgumentParser(description='builder')
    parser.add_argument('-c', '--category', choices=['table', 'lexicon', 'keyboard'], nargs='?')
    parser.add_argument('-t', '--target', choices=['json', 'db'], nargs='?')
    parser.add_argument('-i', '--input_dir', help='dir', nargs='?')
    parser.add_argument('-o', '--output_dir', help='dir', nargs='?')

    args = parser.parse_args()
    # print('args:', args)

    match args.category:
        case 'table':
            if args.target == 'db':
                _table_db(args.input_dir, args.output_dir)
        case 'lexicon':
            if args.target == 'db':
                _lexicon_db(args.input_dir, args.output_dir)
        case 'keyboard':
            pass
        case _:
            print("No matching category")
            pass


def _lexicon_db(input_dir: str, output_dir: str):
    if not os.path.exists(input_dir):
        sys.exit(f"[404]: {input_dir}")
    if not os.path.exists(output_dir):
        sys.exit(f"[404]: {output_dir}")

    delete_old_file = prompt("Delete old file before build?", False)
    for path in os_sorted(list(pathlib.Path(input_dir).glob("*.csv"))):
        # filename = pathlib.Path(path).stem
        filename = pathlib.Path(path).name
        output_path = f"{output_dir}/{filename}.db"

        if os.path.exists(output_path):
            if delete_old_file:
                # print(f"[X] delete {outputPath}")
                os.remove(output_path)
            else:
                print(f"[X] {filename}")
                continue

        if filename.startswith('_'):
            continue

        cmd = f"{RUN} lexicon2db.py -i {path} -o {output_path}"
        # print(f"-> cmd: {cmd}")
        run(cmd)

def _table_db(input_dir: str, output_dir: str):
    if not os.path.exists(input_dir):
        sys.exit(f"[404]: {input_dir}")
    if not os.path.exists(output_dir):
        sys.exit(f"[404]: {output_dir}")

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

    delete_old_file = prompt("Delete old file before build?", False)
    for path in os_sorted(list(pathlib.Path(input_dir).glob("*.cin"))):
        # filename = pathlib.Path(path).stem
        filename = pathlib.Path(path).name
        output_path = f"{output_dir}/{filename}.db"

        if os.path.exists(output_path):
            if delete_old_file:
                # print(f"[X] delete {outputPath}")
                os.remove(output_path)
            else:
                print(f"[X] {filename}")
                continue

        if filename.startswith('_') or filename in excludes:
            continue

        # print(f"-> {filename}")
        cmd = f"{RUN} cin2db.py -i {path} -o {output_path}"
        if filename.startswith("array30"):
            cmd = f"{cmd} -e array"
        # print(f"-> cmd: {cmd}")
        run(cmd)

    pass

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
