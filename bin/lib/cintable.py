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
from enum import IntEnum

from lib.util import trim, chunks

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

    def __init__(self, path, level: CinTableParseLevel = CinTableParseLevel.No):
        self.path = path
        self.description = ""
        self.info = {}
        self.keyname = {}
        self.chardef = []
        self.duplicateChardef = []
        self.unknownTags = []
        if path and level != CinTableParseLevel.No:
            self.parse(level = level)

    def __str__(self):
        return f"""Name: {self.getName()}
Info: {self.info}
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

    def error(self, msg):
        print(msg)
        sys.exit()

    def parse(self, level: CinTableParseLevel = CinTableParseLevel.Header):
        if not self.fileExists():
            self.error("File not exists")

        with open(self.path, "r") as fp:

            currentSection = None
            ignoreSection = None
            acceptComments = True
            disable = False if level > 2 else True

            for chunk in chunks(fp.readlines(), size = 50000, max = 0):
                for line in tqdm(chunk, desc = f"CIN[]", unit = 'MB', unit_scale = True, ascii = True, disable = disable):

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
                    items = re.split('[\s\t]{1}', line, 1)
                    # if len(items) < 2:
                    #     continue

                    key = trim(items[0]).lower()
                    value = trim((items[1:2] or ('', ''))[0])
                    # print(f"{key} => _{value}_")

                    if acceptComments and value == "begin":
                        # once any section began, ignore all comments for "description"
                        acceptComments = False

                    if key in self.definedSections:
                        if currentSection == key and value == "end":
                            currentSection = None
                            ignoreSection = None
                            # print(f"end section: {key}")
                        else:
                            if level == CinTableParseLevel.Header and key == "%chardef":
                                currentSection = None
                                ignoreSection = key
                                # normally this should be fine
                                break
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
                            # print(f"[?] Unknown tag: {key} {value}")
                            self.unknownTags.append(key)
                            continue

                        self.info[key[1:]] = value
                        continue

                    if currentSection == "%keyname":
                        self.keyname[key] = value
                        continue

                    if currentSection == "%chardef" and value:
                        # self.chardef[key] = value
                        self.chardef.append([key, value])

        self.description = trim(self.description, space = True)

        if level == CinTableParseLevel.Validate:
            self.validate()

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
            if self.info[tag]:
                return self.info[tag]
        return "Noname"

    def validate(self):
        self.removeDuplicateCharde

