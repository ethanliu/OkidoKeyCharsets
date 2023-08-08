#!/usr/bin/env python
#
# version: 0.1.0
# autor: Ethan Liu
#
# OkidoKey/Frankie resources generator

import argparse
import importlib
import sys, os, glob, re, shutil
import sqlite3, json
from datetime import datetime
from lib.cintable import CinTable

uu = importlib.import_module("lib.util")
cwd = uu.dir(__file__ + "/../")

def splitFile(filename):
    path1 = f"{cwd}/db/{filename}"
    path2 = f"{cwd}/rawdata/gitee/db/{filename}"

    # print('---')
    # print(path1)
    # print(path2)

    for file in glob.glob(f"{path2}.*"):
        os.remove(file)

    shutil.copy(path1, path2)
    uu.call([f"{cwd}/bin/LoveMachine -s {path2}"])
    os.remove(path2)

def createJsonFile(path, content):
    print(uu.color(f"{os.path.basename(path)} created.", fg = 'green'))
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

    for path in sorted(glob.glob(f"{charsetPath}/*.charset.json")):
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

            if 'keynameType' in item:
                jsondata['charsets'][item['name']]['keynameType'] = item['keynameType']

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
        'datatables': [],
        'splits': {},
    }

    for path in sorted(glob.glob(f"{dbPath}/*.cin.db")):
        dbFilename = os.path.basename(path)
        filename = dbFilename.replace('.db', '')
        splitFile(dbFilename)
        cin = CinTable(f"{tablePath}/{filename}", level = 1)
        content = {
            'ename': cin.info.get('ename') or '',
            'cname': cin.info.get('cname') or '',
            'name': cin.info.get('name') or '',
            'cin': f"table/{filename}",
            'db': f"db/{dbFilename}",
            'license': cin.description,
        }
        # print(content)
        jsondata['datatables'].append(content)

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

    for path in sorted(glob.glob(f"{dbPath}/lexicon-*.csv.db")):
        dbFilename = os.path.basename(path)
        filename = dbFilename.replace('lexicon-', '').replace('.db', '')
        txtPath = f"{lexiconPath}/{filename}.txt"

        if not os.path.exists(txtPath):
            print("File not found: {txtPath}")
            continue

        splitFile(dbFilename)

        reader = open(f"{lexiconPath}/{filename}.txt", 'r')
        template = reader.read()
        reader.close()

        tmp = template.split("\n")
        name = tmp[0]
        tmp = ''

        # sample
        db = sqlite3.connect(path)
        cursor = db.cursor()
        # cursor.execute("SELECT `phrase`, `pinyin` FROM `lexicon`, `pinyin` WHERE `lexicon`.`pinyin_id` = `pinyin`.`rowid` ORDER BY RANDOM() LIMIT 10")
        cursor.execute("SELECT `phrase`, `pinyin` FROM `lexicon` WHERE 1 ORDER BY RANDOM() LIMIT 10")
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
    argParser = argparse.ArgumentParser(description='Resource files generator')
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
