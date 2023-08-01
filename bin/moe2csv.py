#!/usr/bin/env python
#
# version: 0.0.1
# autor: Ethan Liu
#
# ref:
# https://language.moe.gov.tw/001/Upload/Files/site_content/M0001/respub/index.html
#

import argparse
import sys, os
import csv
import re
import codecs
from tqdm import tqdm
from lib.util import chunks

kAccentsMap = {
    u'ā': u'a', u'ɑ̄': u'a', u'ē': u'e', u'ī': u'i', u'ō': u'o', u'ū': u'u', u'ǖ': u'u',
    u'Ā': u'A', u'Ē': u'E', u'Ī': u'I', u'Ō': u'O', u'Ū': u'U', u'Ǖ': u'U',
    u'á': u'a', u'ɑ́': u'a', u'é': u'e', u'í': u'i', u'ó': u'o', u'ú': u'u', u'ǘ': u'u',
    u'Á': u'A', u'É': u'E', u'Í': u'I', u'Ó': u'O', u'Ú': u'U', u'Ǘ': u'U',
    u'ǎ': u'a', u'ɑ̌': u'a', u'ě': u'e', u'ǐ': u'i', u'ǒ': u'o', u'ǔ': u'u', u'ǚ': u'u',
    u'Ǎ': u'A', u'Ě': u'E', u'Ǐ': u'I', u'Ǒ': u'O', u'Ǔ': u'U', u'Ǚ': u'U',
    u'à': u'a', u'ɑ̀': u'a', u'è': u'e', u'ì': u'i', u'ò': u'o', u'ù': u'u', u'ǜ': u'u',
    u'À': u'A', u'È': u'E', u'Ì': u'I', u'Ò': u'O', u'Ù': u'U', u'Ǜ': u'U',
    u'a': u'a', u'ɑ': u'a', u'e': u'e', u'i': u'i', u'o': u'o', u'u': u'u', u'ü': u'u',
    u'A': u'A', u'E': u'E', u'I': u'I', u'O': u'O', u'U': u'U', u'Ü': u'U',
}

kStripMpsSpaceSeparate = True
kMinPhraseLength = 2
kMps1Set = set(' ˇˊˋ˙ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙㄚㄛㄜㄝㄞㄟㄠㄡㄢㄣㄤㄥㄦㄧㄨㄩ')
kPattern1 = r"[（\(][變|一|二|三|四|五|六|語音|讀音|又音|\d]+[）\)]|<br>"

def asciify(error):
    return kAccentsMap[error.object[error.start]], error.end

def trimMps1(str):
    return ''.join(c for c in str if c in kMps1Set)

def trimMps2(str):
    str = str.strip()
    try:
        str = str.encode('ascii', 'asciify').decode()
    except:
        pass
    return str

def indexExists(list, index):
    try:
        list[index]
        return True
    except IndexError:
        return False

def uniqueList(rows):
    return list(dict.fromkeys(filter(None, rows)))

def parse(inputPath, outputPath):

    filename = os.path.basename(inputPath)
    column = []
    contents = ""

    with open(inputPath) as fp:
        reader = csv.reader(fp, delimiter = ',')
        for chunk in chunks(reader, max = 0):
            for row in tqdm(chunk, desc = f"{filename}[]", unit = 'MB', unit_scale = True, ascii = True):
                if not column:
                    column = row
                    continue

                # code = row[0].strip()
                phrase = row[1].strip()

                if not phrase or len(phrase) < kMinPhraseLength:
                    # print(f"Ignore short phrase: {phrase}")
                    continue

                if ".gif" in phrase or ".png" in phrase:
                    # TODO: unicode mapping
                    # print(f"Ignore legacy phrase: {phrase}")
                    continue

                mps1 = ' '.join([node.strip() for node in row[2].split('\u3000')])
                mps1 = re.split(kPattern1, trimMps1(mps1))

                mps2 = ' '.join([node.strip() for node in row[3].split('\u3000')])
                mps2 = [trimMps2(node) for node in re.split(kPattern1, mps2)]

                if indexExists(row, 4):
                    extra = row[4].replace('<br>', '\u3000')
                    extra = ' '.join([node.strip() for node in extra.split('\u3000')])
                    extra = ' '.join(list(filter(None, [node.strip() for node in re.split(kPattern1, extra)])))
                    extra = [node.strip() for node in extra.split()]

                    for item in extra:
                        item = item.strip()
                        try:
                            item = item.encode('ascii', 'asciify').decode()
                            mps2.append(item)
                        except:
                            mps1.append(trimMps1(item))

                mps1 = uniqueList(mps1)
                mps2 = uniqueList(mps2)

                #     print(phrase)
                #     print(f"mps1: {row[2]} => {mps1}")
                #     print(f"mps2: {row[3]} => {mps2}")

                for mps in mps2:
                    # print(f"{phrase}\t0\t{mps}")
                    if kStripMpsSpaceSeparate:
                        contents += f"{phrase}\t0\t{''.join(mps.split())}\n"
                    else:
                        contents += f"{phrase}\t0\t{mps}\n"

        # fp.close()

    # if not outputPath:
    #     print(contents)
    #     return

    with open(outputPath, 'w') as fp:
        fp.write(contents)
        fp.close()


def main():
    argParser = argparse.ArgumentParser(description='Convert to lexicon-CSV-format from the original excel/csv format')
    # argParser.add_argument('-c', '--category', choices=['concised', 'idoms', 'revised'], help='Lexicon category')
    argParser.add_argument('-i', '--input', help='Original csv file path')
    argParser.add_argument('-o', '--output', default='', help='Lexicon format csv file path')

    args = argParser.parse_args()
    # print(args, len(sys.argv))

    if not os.path.exists(args.input):
        sys.exit(f"File not found: {args.input}")

    codecs.register_error('asciify', asciify)

    parse(args.input, args.output)

    # if args.category == "concised":
    #     parseConcised(args.path, args.output)
    # elif args.category == "idoms":
    #     parseConcised(args.path, args.output)
    # elif args.category == "revised":
    #     parseConcised(args.path, args.output)

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
