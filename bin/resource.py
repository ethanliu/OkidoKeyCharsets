#!/usr/bin/env python
#
# version: 0.0.1
# autor: Ethan Liu
#
# OkidoKey/Frankie resources generator

import argparse
import importlib
import sys, os, glob, re
import sqlite3, json
from datetime import datetime

uu = importlib.import_module("lib.util")
cwd = uu.dir(__file__ + "/../")

def createJsonFile(path, content):
    with open(path, 'w') as f:
        f.write(json.dumps(content, ensure_ascii = False, indent = 4, sort_keys = True))
        f.close()


def createKeyboard():
    outputPath = f"{cwd}/KeyboardLayouts.json"
    charsetPath = f"{cwd}/charset"

    jsondata = {
        'version': (datetime.now()).strftime(f'%Y%m%d%H%M%S'),
        "charsets": {},
    }

    for path in glob.glob(f"{charsetPath}/*.charset.json"):
        file = open(path, 'r')
        data = json.load(file)
        file.close()
        # print(path)
        for item in data:

            if not 'name' in item:
                print("name missing")
                continue

            if not 'charsets' in item:
                print("charsets missing")
                continue

            if item['name'] in jsondata['charsets']:
                print(f"[exists] {item['name']}")
                continue

            jsondata['charsets'][item['name']] = {
                'description': item['description'] or '',
                'charsets': item['charsets']
            }

            if 'flicks' in item:
                jsondata['charsets'][item['name']]['flicks'] = item['flicks']

    createJsonFile(outputPath, jsondata)


def createTable():
    outputPath = f"{cwd}/DataTables.json"
    dbPath = f"{cwd}/db"
    tablePath = f"{cwd}/table"
    giteeRepoPath = f"{cwd}/rawdata/gitee/db"

    jsondata = {
        'version': (datetime.now()).strftime(f'%Y%m%d%H%M%S'),
        'databases': [],
        'splits': {},
    }

    for path in glob.glob(f"{dbPath}/*.cin.db"):
        filename = os.path.basename(path).replace('.db', '')

        # if filename.startswith('lexicon-'):
        #     continue

        if not os.path.exists(f"{tablePath}/{filename}"):
            print(f"File not found: {filename}")
            continue

        # print(f"{filename}")
        with open(f"{tablePath}/{filename}", 'r') as reader:
            content = {
                'ename': '',
                'cname': '',
                'name': '',
                'cin': f"table/{filename}",
                'db': f"db/{filename}.db",
                'license': '',
            }

            for row in reader.readlines():
                if row.startswith('#'):
                    row = row.replace('#', '').strip()
                    if not row or row == '':
                        continue
                    content['license'] += f"{row}\n"

                elif row.startswith('%'):
                    row = uu.trim(row, '#')
                    if not row or row == '':
                        continue
                    items = re.split('[\s|\t]{1}', row, 1)
                    if len(items) < 2:
                        # print(f"[?] ignore: {row}")
                        continue
                    key = uu.trim(items[0])
                    value = uu.trim(items[1])
                    # print(f"[i] {key[1:]} = {value}")
                    # proccess only what we need
                    match key[1:]:
                        case 'ename':
                            content['ename'] = value
                        case 'cname':
                            content['cname'] = value
                        case 'name':
                            content['name'] = value

                else:
                    # print(f"[?] ignore: {row}")
                    pass

                if row.startswith('%keyname') or row.startswith('%charset'):
                    # print("--- escape")
                    break

            reader.close()
            jsondata['databases'].append(content)

        # splits
        list = glob.glob(f"{giteeRepoPath}/{filename}*")
        # print(f"{filename}: {len(list)}")

        if not filename in jsondata['splits']:
            jsondata['splits'][filename] = {}

        if not 'gitee' in jsondata['splits'][filename]:
            jsondata['splits'][filename]['gitee'] = len(list)

        # jsondata['splits'][filename]['gitee'] = len(list)

    createJsonFile(outputPath, jsondata)

def createLexicon():
    outputPath = f"{cwd}/Lexicon.json"
    dbPath = f"{cwd}/db"
    lexiconPath = f"{cwd}/lexicon"
    giteeRepoPath = f"{cwd}/rawdata/gitee/db"

    jsondata = {
        'version': (datetime.now()).strftime(f'%Y%m%d%H%M%S'),
        'resources': [],
        'splits': {},
    }

    for path in glob.glob(f"{dbPath}/lexicon-*.csv.db"):
        dbFilename = os.path.basename(path)
        filename = dbFilename.replace('lexicon-', '').replace('.db', '')
        txtPath = f"{lexiconPath}/{filename}.txt"
        if not os.path.exists(txtPath):
            print("File not found: {txtPath}")
            continue

        reader = open(f"{lexiconPath}/{filename}.txt", 'r')
        template = reader.read()
        reader.close()

        tmp = template.split("\n")
        name = tmp[0]
        tmp = ''

        # sample
        db = sqlite3.connect(path)
        cursor = db.cursor()
        cursor.execute("SELECT `phrase`, `pinyin` FROM `lexicon`, `pinyin` WHERE `lexicon`.`pinyin_id` = `pinyin`.`rowid` ORDER BY RANDOM() LIMIT 10")
        result = cursor.fetchall()
        template += "\n\n詞庫範例\n=======\n"
        for item in result:
            phrase = item[0] or ''
            pinyin = item[1] or ''
            template += f"{phrase} {pinyin}\n"

        db.close()


        # print(template)
        jsondata['resources'].append({
            'name': name,
            'db': f"db/{dbFilename}",
            'description': template,
        })

        # splits
        list = glob.glob(f"{giteeRepoPath}/{dbFilename}*")
        # print(f"{filename}: {len(list)}")

        if not dbFilename in jsondata['splits']:
            jsondata['splits'][dbFilename] = {}

        if not 'gitee' in jsondata['splits'][dbFilename]:
            jsondata['splits'][dbFilename]['gitee'] = len(list)


    createJsonFile(outputPath, jsondata)

def main():
    argParser = argparse.ArgumentParser(description='ChineseVariant.db generator')
    argParser.add_argument('-c', '--category', required = True, choices=['keyboard', 'lexicon', 'table'], help='Resource category')

    args = argParser.parse_args()
    # print(args, len(sys.argv))

    match args.category:
        case 'keyboard':
            createKeyboard()
        case 'table':
            createTable()
        case 'lexicon':
            createLexicon()

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
