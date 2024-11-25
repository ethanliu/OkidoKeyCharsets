#!/usr/bin/env python
#
# autor: Ethan Liu
#
# pinyin helper
#

import os, sys
import sqlite3
from lib.util import list_flatten, db_get_one
from pypinyin import lazy_pinyin, Style

# issue: not helping at all
# from pypinyin_dict.phrase_pinyin_data import cc_cedict
# cc_cedict.load()

BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))
DIST_DIR = f"{BASE_DIR}/dist/queue"

class PinyinQuery:
    conn = None
    def __init__(self, query: bool = True):
        if query:
            self.conn = sqlite3.connect(":memory:")
            self.cursor = self.conn.cursor()
            self.attach_databases()

    def close(self):
        if self.conn:
            self.conn.close()

    def attach_databases(self):
        if not self.cursor:
            return

        paths = {
            "idioms": f"{DIST_DIR}/lexicon/moe-idioms.csv.db",
            "concised": f"{DIST_DIR}/lexicon/moe-concised.csv.db",
            "revised": f"{DIST_DIR}/lexicon/moe-revised.csv.db",
        }

        for alias, path in paths.items():
            if not os.path.exists(path):
                SystemExit("File missing: {path}")
            self.cursor.execute(f"ATTACH DATABASE '{path}' AS {alias}")

    def find(self, phrase: str):
        if not self.cursor:
            return None

        args = {"phrase": phrase}
        queries = [
            "SELECT pinyin FROM idioms.lexicon WHERE phrase = :phrase",
            "SELECT pinyin FROM concised.lexicon WHERE phrase = :phrase",
            "SELECT pinyin FROM revised.lexicon WHERE phrase = :phrase",
        ]

        query = f"""
            SELECT DISTINCT pinyin FROM (
                {' UNION ALL '.join(queries)}
            )
        """
        # print(query)

        result = db_get_one(self.cursor, query, args)

        if result == None:
            result = self.pinyin(phrase)
            # pp1 = pinyin(phrase, heteronym=True, strict=False, style=Style.NORMAL)
            # pp2 = pinyin(phrase, heteronym=False, strict=False, style=Style.NORMAL)

        return result or ""

    def pinyin(self, phrase: str):
        result = "".join(list_flatten(lazy_pinyin(phrase, strict=False, errors='ignore', style=Style.NORMAL)))
        # pp1 = pinyin(phrase, heteronym=True, strict=False, style=Style.NORMAL)
        # pp2 = pinyin(phrase, heteronym=False, strict=False, style=Style.NORMAL)
        return result or ""
