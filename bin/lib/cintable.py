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
from lib.util import trim, chunks, vprint, whitespace

_verbose = False

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
    defined_tags = [
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

        self.duplicate_chardef = []
        self.unknown_tags = []

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
        return f"""Name: {self.get_name()}
Info: {self.meta}
Unknown Tags: {self.unknown_tags}
Total Keyname: {len(self.keyname)}
Total Chardef: {len(self.chardef)}
Total Duplicate Chardef: {len(self.duplicate_chardef)}"""

    def file_exists(self):
        if not self.path:
            return False
        if not os.path.exists(self.path):
            return False
        return True

    def log(self, msg, stop = False):
        vprint(msg, _verbose)
        if stop:
            tqdm.write(msg)
            sys.exit()

    def parse(self):
        if not self.file_exists():
            self.log("File not exists", stop = True)

        filename = os.path.basename(self.path)
        with open(self.path, "r") as fp:

            current_block: Block | None = None
            ignore_block_name = None
            accept_comments = True
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
                        # line = line.lstrip('# ').rstrip('# ')
                        line = trim(line.lstrip('#').rstrip('#'))
                        # if not line:
                        #     continue
                        # ignore comments in charset
                        if accept_comments:
                            self.description += f"{line}\n"
                        continue

                    line = trim(line, '#')
                    items = re.split('[\\s\\t]{1}', line, 1)
                    # if len(items) < 2:
                    #     continue

                    key = trim(items[0]).lower()
                    value = trim((items[1:2] or ('', ''))[0])
                    # print(f"{key} => _{value}_")

                    if accept_comments and (value == "begin" or len(self.meta) > 0):
                        # once any section began, ignore all comments for "description"
                        accept_comments = False

                    try:
                        _block = Block(key)
                        if current_block == _block and value == "end":
                            current_block = None
                            ignore_block_name = None
                            self.log(f"end of block: {key}")
                        else:
                            current_block = _block
                            ignore_block_name = None
                            self.log(f"beginning of block: {key}")
                        continue
                    except:
                        # self.log(f"Invalid block: {key}")
                        pass

                    if not current_block:
                        if ignore_block_name:
                            self.log(f"Ignore block: {ignore_block_name}")
                            continue
                        if key.startswith('%') and (value == 'begin' or value == 'end'):
                            ignore_block_name = key
                            self.log(f"[?] Unknown block: {key}")
                            self.unknown_tags.append(key)
                            continue

                        if not key in self.defined_tags:
                            self.log(f"[?] Unknown tag: {key} {value}")
                            self.unknown_tags.append(key)
                            continue

                        self.meta[key[1:]] = value
                        continue

                    if current_block == Block.Keyname:
                        self.log(f"-> keyname: {key} {value}")
                        self.keyname[key] = value
                    else:
                        if disable:
                            stop = True
                            break
                        if current_block and not current_block in self.blocks:
                            # tqdm.write(f"<-- {currentBlock} / {self.blocks}")
                            # continue instead of stop incase charset is not the first block
                            continue
                        if current_block == Block.Chardef and current_block in self.blocks and value:
                            # self.log(f"-> chardef: {key} {value}")
                            self.chardef.append([key, value])
                        elif current_block == Block.Special and current_block in self.blocks and value:
                            # self.log(f"-> chardef: {key} {value}")
                            self.extra['special'].append([key, value])
                        elif current_block == Block.Shortcode and current_block in self.blocks and value:
                            # self.log(f"-> chardef: {key} {value}")
                            self.extra['shortcode'].append([key, value])

        self.description = re.sub(r'([-=]{3,})\n', '---\n', self.description)
        self.description = trim(whitespace(self.description), space = True)

        # if level == CinTableParseLevel.Validate:
        #     self.validate()
        # print(self)

    def remove_duplicate_chardef(self):
        unique = []
        duplicate = []
        for item in tqdm(self.chardef, unit = 'MB', unit_scale = True, ascii = True, desc = f"[CIN]"):
        # for item in self.chardef:
            if item not in unique:
                unique.append(item)
            else:
                duplicate.append(item)
        self.chardef = unique
        self.duplicate_chardef = duplicate

    def get_name(self):
        tags = ["cname", "tcname", "scname", "name"]
        for tag in tags:
            # print(self.info.get(tag))
            if not self.meta.get(tag) is None:
                return self.meta[tag]
        return "Noname"

    def validate(self):
        self.remove_duplicate_chardef

