#!/usr/bin/env python
#
# version: 0.1.0
# autor: Ethan Liu
#
# CIN Table Parser
#

import sys
import os
import re
# from collections import OrderedDict
from tqdm import tqdm
from enum import Enum

from lib.util import trim, chunks, vprint

# class CinTableParseLevel(IntEnum):
#     No = 0
#     Header = 1
#     Full = 2
#     Validate = 3

# Using auto with StrEnum results in the lower-cased member name as the value.
class Block(Enum):
    Keyname = "%keyname"
    Chardef = "%chardef"
    Shortcode = "%shortcode"
    Special = "%special"

class CinTable:
    definedTags = [
        '%gen_inp',
        '%encoding',
        '%name',
        '%endkey',
        '%selkey',
        '%cname',
        '%ename',
        '%tcname',
        '%scname',
        '%locale',
    ]

    def __init__(self, path, blocks):
        self.path = path
        self.blocks = blocks # or [Block.Chardef]

        self.duplicateChardef = []
        self.unknownTags = []

        self.description = ""
        self.meta = {}
        self.keyname = {}
        self.chardef = []
        self.extra = {
            'shortcode': [],
            'special': [],
        }

        if path:
            # tqdm.write(f"parsing: {path}, blocks: {blocks}")
            self.parse()

    def __str__(self):
        return f"""Name: {self.getName()}
Info: {self.meta}
Unknown Tags: {self.unknownTags}
Total Keyname: {len(self.keyname)}
Total Chardef: {len(self.chardef)}
Total Duplicate Chardef: {len(self.duplicateChardef)}"""

    def fileExists(self):
        if not self.path:
            return False
        if not os.path.exists(self.path):
            return False
        return True

    def log(self, msg, stop = False):
        # verbose = True
        # vprint(msg, verbose)
        if stop:
            tqdm.write(msg)
            sys.exit()

    def parse(self):
        if not self.fileExists():
            self.log("File not exists", stop = True)

        filename = os.path.basename(self.path)
        with open(self.path, "r") as fp:

            currentBlock: Block | None = None
            ignoreBlockName = None
            acceptComments = True
            stop = False
            disable = False if len(self.blocks) > 0 else True

            for chunk in chunks(fp.readlines(), size = 50000, max = 0):
                if stop:
                    break
                for line in tqdm(chunk, desc = f"{filename}", unit = 'MB', unit_scale = True, ascii = True, disable = disable):
                    if stop:
                        break

                # for line in tqdm(fp.readlines(), unit = 'MB', unit_scale = True, ascii = True, desc = f"[CIN]"):
                # for line in fp.readlines():
                    line = trim(line)
                    if not line:
                        continue
                    # if line.startswith('#') and not self.info:
                    if line.startswith('#'):
                        # line = line.replace('#', '').strip()
                        line = line.lstrip('# ').rstrip('# ')
                        # if not line:
                        #     continue
                        # ignore comments in charset
                        if acceptComments:
                            self.description += f"{line}\n"
                        continue

                    line = trim(line, '#')
                    items = re.split('[\\s\\t]{1}', line, 1)
                    # if len(items) < 2:
                    #     continue

                    key = trim(items[0]).lower()
                    value = trim((items[1:2] or ('', ''))[0])
                    # print(f"{key} => _{value}_")

                    if acceptComments and value == "begin":
                        # once any section began, ignore all comments for "description"
                        acceptComments = False

                    try:
                        _block = Block(key)
                        if currentBlock == _block and value == "end":
                            currentBlock = None
                            ignoreBlockName = None
                            self.log(f"end of block: {key}")
                        else:
                            currentBlock = _block
                            ignoreBlockName = None
                            self.log(f"beginning of block: {key}")
                        continue
                    except:
                        # self.log(f"Invalid block: {key}")
                        pass

                    if not currentBlock:
                        if ignoreBlockName:
                            self.log(f"Ignore block: {ignoreBlockName}")
                            continue
                        if key.startswith('%') and (value == 'begin' or value == 'end'):
                            ignoreBlockName = key
                            self.log(f"[?] Unknown block: {key}")
                            self.unknownTags.append(key)
                            continue

                        if not key in self.definedTags:
                            self.log(f"[?] Unknown tag: {key} {value}")
                            self.unknownTags.append(key)
                            continue

                        self.meta[key[1:]] = value
                        continue

                    if currentBlock == Block.Keyname:
                        # self.log(f"-> keyname: {key} {value}")
                        self.keyname[key] = value
                    else:
                        if currentBlock and not currentBlock in self.blocks:
                            # tqdm.write(f"<-- {currentBlock} / {self.blocks}")
                            # continue instead of stop incase charset is not the first block
                            continue
                            # stop = True
                            # break
                        if currentBlock == Block.Chardef and currentBlock in self.blocks and value:
                            # self.log(f"-> chardef: {key} {value}")
                            self.chardef.append([key, value])
                        elif currentBlock == Block.Special and currentBlock in self.blocks and value:
                            # self.log(f"-> chardef: {key} {value}")
                            self.extra['special'].append([key, value])
                        elif currentBlock == Block.Shortcode and currentBlock in self.blocks and value:
                            # self.log(f"-> chardef: {key} {value}")
                            self.extra['shortcode'].append([key, value])

        self.description = trim(self.description, space = True)
        # if level == CinTableParseLevel.Validate:
        #     self.validate()
        # print(self)

    def removeDuplicateCharde(self):
        unique = []
        duplicate = []
        for item in tqdm(self.chardef, unit = 'MB', unit_scale = True, ascii = True, desc = f"[CIN]"):
        # for item in self.chardef:
            if item not in unique:
                unique.append(item)
            else:
                duplicate.append(item)
        self.chardef = unique
        self.duplicateChardef = duplicate

    def getName(self):
        tags = ["cname", "tcname", "scname", "name"]
        for tag in tags:
            # print(self.info.get(tag))
            if not self.meta.get(tag) is None:
                return self.meta[tag]
        return "Noname"

    def validate(self):
        self.removeDuplicateCharde

