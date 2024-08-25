#!/usr/bin/env python
#
# version: 0.1.0
# autor: Ethan Liu
#
# Unihan char
#

# import xml.etree.ElementTree as xet
from enum import IntEnum
from lib.util import strip_accents, trim

# https://www.unicode.org/reports/tr38/#kCompatibilityVariant


# or ignore range? F900–FAFF，2F800–2FA1F
class Classified(IntEnum):
    Common = 1
    LessCommon = 2
    Rare = 3
    Newly = 10
    # for sorting friendly purpose, giving a large number instead of zero
    Unclassified = 99

    @staticmethod
    def from_category(category):
        match category:
            case 'A':
                return Classified.Common
            case 'B':
                return Classified.LessCommon
            case 'C':
                return Classified.Rare
            case 'N':
                return Classified.Newly
            case _:
                return Classified.Unclassified

# cp="3400"
# kCompatibilityVariant=""
# kRSUnicode="1.4"
# kIRG_GSource="GKX-0078.01"
# kIRG_TSource="T6-222C"
# kIRG_JSource="JA-2121"
# kIRG_KSource=""
# kIRG_KPSource=""
# kIRG_VSource=""
# kIRG_HSource=""
# kIRG_USource=""
# kIRG_MSource=""
# kIRG_UKSource=""
# kIRG_SSource=""
# kCantonese="jau1"
# kDefinition="(same as U+4E18 丘) hillock or mound"
# kHanYu="10015.030"
# kMandarin="qiū"
# kCangjie="TM"
# kSemanticVariant="U+4E18"
# kKangXi="0078.010"
# kIRGHanyuDaZidian="10015.030"
# kIRGKangXi="0078.010"
# kTotalStrokes="5"

class UnihanChar:
    def __init__(self, node):
        self.classified = Classified.Unclassified
        self.text = ""
        self.codepoint = ""
        self.definition = ""
        self.mandarin = ""
        self.strange = ""
        # self.fenn = ""
        self.tsource = ""
        # kTotalStrokes
        # The total number of strokes in the character (including the radical). When there are two values, then the first is preferred for zh-Hans (CN) and the second is preferred for zh-Hant (TW). When there is only one value, it is appropriate for both.
        self.strokes = 0
        # kFrequency: [1-5]
        # A rough frequency measurement for the character based on analysis of traditional Chinese USENET postings; characters with a kFrequency of 1 are the most common, those with a kFrequency of 2 are less common, and so on, through a kFrequency of 5.
        self.frequency = 0
        # kGradeLevel: [1-6], 1: easy, 6: hard
        # The primary grade in the Hong Kong school system by which a student is expected to know the character; this data is derived from 朗文初級中文詞典, Hong Kong: Longman, 2001.
        self.gradeLevel = 0
        self.score = 0
        self.semanticVariant = []
        self.simplifiedVariant = []
        self.traditionalVariant = []
        self.parse(node)


    def __str__(self):
        # \tStroke: {self.stroke}\tFreq: {self.frequency}\tLevel: {self.gradeLevel}
        return f"{self.codepoint} => {self.text}\tTS: {self.tsource}\tStrange: {self.strange}\tScore: {self.score}\tMandarin: {self.mandarin}\tHans: {self.simplifiedVariant}\tHant: {self.traditionalVariant}\tSeg: {self.semanticVariant}\t:def: {self.definition}"

    def parse(self, node):
        self.codepoint = node.get('cp')
        self.text = trim(chr(int(self.codepoint, 16)))

        self.frequency = int(node.get('kFrequency') or '0')
        self.gradeLevel = int(node.get('kGradeLevel') or '0')
        # self.pinyin = node.get('kHanyuPinyin')
        # kMandarin: [a-z\x{300}-\x{302}\x{304}\x{308}\x{30C}]+
        self.mandarin = node.get('kMandarin')
        if self.mandarin:
            self.mandarin = strip_accents(self.mandarin)
        # kPhonetic: [1-9][0-9]{0,3}[A-Dx]?[*+]?
        # self.phonetic = node.get('kPhonetic')
        # kSpoofingVariant
        self.strange = node.get('kStrange')
        # self.fenn = node.get('kFenn')
        self.tsource = node.get('kIRG_TSource')

        if node.get('kTotalStrokes'):
            strokes = node.get('kTotalStrokes').split()
            # preferred for zh-Hant (TW)
            self.stroke = int(strokes[-1])

        # kSimplifiedVariant: U\+[23]?[0-9A-F]{4}
        # self.simplifiedVariant = node.get('kSimplifiedVariant')
        # if self.simplifiedVariant:
        #     self.simplifiedVariant = chr(int(self.simplifiedVariant[2:], 16))

        if node.get('kDefinition'):
            self.definition = node.get('kDefinition')

        if node.get('kSimplifiedVariant'):
            # self.simplifiedVariant = []
            items = node.get('kSimplifiedVariant').split()
            for item in items:
                c = trim(chr(int(item[2:], 16)))
                # if c == self.text:
                #     continue
                self.simplifiedVariant.append(c)

        if node.get('kTraditionalVariant'):
            # self.traditionalVariant = []
            items = node.get('kTraditionalVariant').split()
            for item in items:
                c = trim(chr(int(item[2:], 16)))
                # if c == self.text:
                #     continue
                self.traditionalVariant.append(c)
            # self.traditionalVariant.reverse()
            # self.traditionalVariant.sort()
            # if len(self.traditionalVariant) > 1:
            #     print(self.traditionalVariant)
        # self.traditionalVariant = chr(int(self.traditionalVariant[2:], 16))

        if node.get('kSemanticVariant'):
            self.semanticVariant = node.get('kSemanticVariant')

        # score
        score = 0
        if self.gradeLevel:
            score += 7 - self.gradeLevel
        if self.frequency:
            score += 6 - self.frequency
        if self.mandarin:
            score += 1
        if not self.strange:
            score += 1
        if not self.traditionalVariant:
            score += 1
        self.score = score

