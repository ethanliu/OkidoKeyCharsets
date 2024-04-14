#!/usr/bin/env python
#
# version: 0.0.2
# autor: Ethan Liu
#
# misc purpose toolkit
#

import argparse
from logging import shutdown
import shutil
import sys, os, importlib
import glob
from tqdm import tqdm
# from time import sleep

uu = importlib.import_module("lib.util")

# define lovemachine
# 	$(eval path1 := "db/$(strip ${1})")
# 	$(eval path2 := "${GITEE_REPO_PATH}/db/$(strip ${1})")
# 	@-rm ${path2}.*
# 	@cp ${path1} ${path2}
# 	@bin/LoveMachine -s ${path2}
# 	@-rm ${path2}
# endef

cwd = uu.dir(__file__ + "/../")

def peformGitee(filename):
    print(f"[check] {filename}")
    # path1 = f"{cwd}/db/{filename}"
    # path2 = f"{cwd}/rawdata/gitee/db/{filename}"

    # for file in glob.glob(f"{path2}.*"):
    #     os.remove(file)

    # shutil.copy(path1, path2)
    # uu.call([f"{cwd}/bin/LoveMachine -s {path2}"])
    # os.remove(path2)

def performDiff(args):
    baseFilePath = args.get(0, None)
    targetFilePath = args.get(1, None)

    if baseFilePath == None:
        print(f"Missing base file")
        return

    if targetFilePath == None:
        print(f"Missing target file")
        return




def main():
    argParser = argparse.ArgumentParser(description='Misc purpose toolkit')
    argParser.add_argument('-t', '--target', choices=['diff'], help='target/action')
    argParser.add_argument('params', type = str, nargs = '+', help='Any arguments')

    args = argParser.parse_args()
    # print(args, len(sys.argv))
    # sys.exit(0)

    if args.target == 'diff':
        performDiff(dict(enumerate(args.params)))

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
