#!/usr/bin/env python
#
# version: 0.0.1
# autor: Ethan Liu
#
# CIN Table Parser
#

import sys
import os
import re
# from collections import OrderedDict
from tqdm import tqdm
from enum import IntEnum

from lib.util import trim

class CinTableParseLevel(IntEnum):
    No = 0
    Header = 1
    Full = 2
    Validate = 3

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
    definedSections = [
        '%keyname',
        '%chardef',
    ]

    description = ""
    info = {}
    keyname = {}
    chardef = []
    duplicateChardef = []
    unknownTags = []

    def __init__(self, path, level: CinTableParseLevel = CinTableParseLevel.No):
        self.path = path
        if path and level != CinTableParseLevel.No:
            self.parse(level = level)

    def __str__(self):
        return f"""info: {self.info}
unknown tags: {self.unknownTags}
total keyname: {len(self.keyname)}
total chardef: {len(self.chardef)}
total duplicate chardef: {len(self.duplicateChardef)}"""

    def fileExists(self):
        if not self.path:
            return False
        if not os.path.exists(self.path):
            return False
        return True

    def error(self, msg):
        print(msg)
        sys.exit()

    def parse(self, level: CinTableParseLevel = CinTableParseLevel.Header):
        # counter = 0
        if not self.fileExists():
            self.error("File not exists")

        with open(self.path, "r") as fp:

            currentSection = None
            ignoreSection = None

            for line in tqdm(fp.readlines(), unit = 'MB', unit_scale = True, ascii = True, desc = f"Parsie CIN"):\
            # for line in fp.readlines():
                line = trim(line)
                if not line:
                    continue
                if line.startswith('#'):
                    line = line.replace('#', '').strip()
                    if not line:
                        continue
                    self.description += f"{line}\n"
                    continue

                items = re.split('[\s\t]{1}', line, 1)
                # if len(items) < 2:
                #     continue

                key = trim(items[0]).lower()
                value = trim((items[1:2] or ('', ''))[0])
                # print(f"{key} => _{value}_")

                if key in self.definedSections:
                    if currentSection == key and value == "end":
                        currentSection = None
                        ignoreSection = None
                        # print(f"end section: {key}")
                    else:
                        if level == CinTableParseLevel.Header and key == "%chardef":
                            currentSection = None
                            ignoreSection = key
                        else:
                            currentSection = key
                            ignoreSection = None
                        # print(f"start section: {key}")
                    continue

                if not currentSection:
                    if ignoreSection:
                        # print(f"Ignore section: {ignoreSection}")
                        continue
                    if key.startswith('%') and (value == 'begin' or value == 'end'):
                        ignoreSection = key
                        # print(f"[?] Unknown section: {key}")
                        self.unknownTags.append(key)
                        continue

                    if not key in self.definedTags:
                        # print(f"[?] Unknown tag: {key}")
                        self.unknownTags.append(key)
                        continue

                    self.info[key[1:]] = value
                    continue

                if currentSection == "%keyname":
                    self.keyname[key] = value
                    continue

                if currentSection == "%chardef":
                    # self.chardef[key] = value
                    self.chardef.append([key, value])

                # counter += 1
                # if counter > 50:
                #     # self.error("end test")
                #     break

        if level == CinTableParseLevel.Validate:
            self.validate()

    def removeDuplicateCharde(self):
        unique = []
        duplicate = []
        for item in tqdm(self.chardef, unit = 'MB', unit_scale = True, ascii = True, desc = f"Validate Chardef"):\
        # for item in self.chardef:
            if item not in unique:
                unique.append(item)
            else:
                duplicate.append(item)
        self.chardef = unique
        self.duplicateChardef = duplicate

    def validate(self):
        self.removeDuplicateCharde

