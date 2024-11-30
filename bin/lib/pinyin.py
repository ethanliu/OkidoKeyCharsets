#!/usr/bin/env python
#
# autor: Ethan Liu
#
# pinyin helper
#

import os, sys
import sqlite3
from lib.util import list_flatten, db_get_one, dir, parent_dir
from pypinyin import lazy_pinyin, Style

# issue: not helping at all
# from pypinyin_dict.phrase_pinyin_data import cc_cedict
# cc_cedict.load()

base_dir = parent_dir(__file__, 2)
build_dir = f"{base_dir}/build/queue"

class PinyinQuery:

    valid_aliases = []

    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()
        self.attach_databases()

    def close(self):
        self.conn.close()

    def attach_databases(self):
        if not self.cursor:
            return

        paths = {
            "idioms": f"{build_dir}/lexicon/moe-idioms.csv.db",
            "concised": f"{build_dir}/lexicon/moe-concised.csv.db",
            "revised": f"{build_dir}/lexicon/moe-revised.csv.db",
            "tcedict": f"{build_dir}/lexicon/cedict-hant.csv.db",
            "scedict": f"{build_dir}/lexicon/cedict-hans.csv.db",
        }

        for alias, path in paths.items():
            if os.path.exists(path):
                self.cursor.execute(f"ATTACH DATABASE '{path}' AS {alias}")
                self.valid_aliases.append(alias)

    def find(self, locale, phrase):
        db_alias = []
        if locale == "hans":
            db_alias = [
                "scedict",
            ]
        else:
            db_alias = [
                "tcedict",
                "tcedict",
                "concised",
                "idioms",
                "revised",
            ]

        db_alias = [x for x in db_alias if x in self.valid_aliases]
        result = self.find_in(db_alias, phrase)
        if result:
            return result

        result = self.pinyin(phrase)
        print(f" ~> [pinyin] {phrase} {result}")
        return result

    def find_in(self, db_alias, phrase):
        for alias in db_alias:
            query = f"SELECT pinyin FROM {alias}.lexicon WHERE phrase = :phrase LIMIT 1"
            args = {'phrase': phrase}
            result = db_get_one(self.cursor, query, args)
            if result:
                print(f" ~> [{alias}] {phrase} {result} ")
                return result
        return None


    def ufind(self, phrase: str):
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
        # cedict 5 tones
        result = " ".join(lazy_pinyin(phrase, strict=False, errors='default', style=Style.TONE3, neutral_tone_with_five=True))

        # result = "".join(list_flatten(lazy_pinyin(phrase, strict=False, errors='default', style=Style.NORMAL)))
        # pp1 = pinyin(phrase, heteronym=True, strict=False, style=Style.NORMAL)
        # pp2 = pinyin(phrase, heteronym=False, strict=False, style=Style.NORMAL)
        return result or ""
