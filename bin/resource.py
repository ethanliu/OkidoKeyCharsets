#!/usr/bin/env python
#
# version: 0.2.0
# autor: Ethan Liu
#
# OkidoKey/Frankie resources generator

import argparse
# import importlib
import sys, os, glob
import re
# import shutil
import sqlite3, json
# from tqdm import tqdm
from datetime import datetime
from lib.cintable import CinTable
from lib.util import trim, parent_dir, trim, color

# uu = importlib.import_module("lib.util")
base_dir = parent_dir(__file__, 1)
build_dir = f"{base_dir}/build"
repos = ["github", "gitee"]

# def splitFile(src, dst, size = 1024):
#     # path1 = f"{cwd}/db/{filename}"
#     # path2 = f"{cwd}/rawdata/gitee/db/{filename}"

#     # print('---')
#     # print(src)
#     # print(dst)

#     for file in glob.glob(f"{dst}.*"):
#         os.remove(file)

#     shutil.copy(src, dst)
#     call([f"{cwd}/bin/LoveMachine -s --{size} {dst}"])
#     os.remove(dst)

def create_json_file(path, content):
    print(color(f"{os.path.basename(path)} created.", fg = 'cyan'))
    with open(path, 'w') as f:
        f.write(json.dumps(content, ensure_ascii = False, indent = 4, sort_keys = True))
        f.close()
    # shutil.copy(path, f"{repos['gitee']}/")
    # shutil.copy(path, f"{repos['github']}/")

def create_keyboard(output_path):
    # outputPath = f"{cwd}/KeyboardLayouts.json"
    charset_path = f"{base_dir}/charset"

    jsondata = {
        'version': (datetime.now()).strftime(f'%Y%m%d%H%M%S'),
        "charsets": {},
    }

    categories = {
        "bpmf": "bpmf",
        "symbol": "symbol",
        "easy": "cangjie",
    }

    for path in sorted(glob.glob(f"{charset_path}/*.charset.json")):
        file = open(path, 'r')
        data = json.load(file)
        file.close()
        # print(path)

        category = os.path.basename(path).split(".")[0]
        for ck, cv in categories.items():
            if category.startswith(ck):
                category = cv

        for item in data:
            name = item['name']
            if not name or name.startswith('_'):
                continue

            # if not 'name' in item:
            #     print("name missing")
            #     continue

            if not 'charsets' in item:
                print("charsets missing")
                continue

            if name in jsondata['charsets']:
                print(f"[exists] {name}")
                continue

            jsondata['charsets'][name] = {
                'description': item['description'] or '',
                'charsets': item['charsets'],
                'category': category
            }

            if 'keynameType' in item:
                jsondata['charsets'][name]['keynameType'] = item['keynameType']

            if 'flicks' in item:
                jsondata['charsets'][name]['flicks'] = item['flicks']

    create_json_file(output_path, jsondata)

# TODO: patching additional description directly
# def patchTableHeaders():
#     srcDir = f"{cwd}/table"
#     for basepath in sorted(glob.glob(f"rawdata/misc/*.cin")):
#         filename = os.path.basename(basepath)
#         srcPath = f"{srcDir}/{filename}"

#         if not os.path.exists(srcPath):
#             continue

#         header = ""
#         with open(basepath, "r") as fp:
#             header = fp.read()

#         if not header:
#             continue

#         with open(srcPath, 'r') as fp:
#             contents = fp.readlines()
#             valid = True
#             targetIndex = 0
#             for index, line in enumerate(contents):
#                 print(f"#{index} -> {line}", end="")
#                 if line == "\n":
#                     continue
#                 if line.startswith('#'):
#                     valid = True
#                     continue
#                 if line.startswith('%gen_inp') and valid:
#                     break

#                 if line == "\n" or line.startswith('#') or line.startswith('%gen_inp') or line.startswith('%encoding'):
#                     continue
#                 print(index)
#                 break
#         print(srcPath)
#         print(index)


def create_table(outputPath):
    target = "table"
    src_path = f"{base_dir}/{target}"
    db_path = f"{base_dir}/build/queue/{target}"

    jsondata = {
        'version': (datetime.now()).strftime(f'%Y%m%d%H%M%S'),
        'datatables': [],
        'splits': {},
    }

    # for path in tqdm(sorted(glob.glob(f"{charsetPath}/*.charset.json")), unit = 'MB', unit_scale = True, ascii = True, desc = ""):
    for path in sorted(glob.glob(f"{db_path}/*.cin.db")):
        dbFilename = os.path.basename(path)
        filename = dbFilename.replace('.db', '')

        # splitFile(f"{dbPath}/{dbFilename}", f"{repos['github']}/{target}/{dbFilename}", 2048)
        # splitFile(f"{dbPath}/{dbFilename}", f"{repos['gitee']}/{target}/{dbFilename}", 1024)

        cin = CinTable(f"{src_path}/{filename}", [])
        content = {
            'ename': cin.meta.get('ename') or '',
            'cname': cin.meta.get('cname') or '',
            'name': cin.meta.get('name') or '',
            'path': f"{target}/{dbFilename}",
            # 'src': f"{target}/{filename}",
            'license': cin.description,
            'category': '',
        }

        category = "misc"
        category_test_string = f"{content['ename']} {content['cname']} {content['name']} {dbFilename}"
        if re.search("(array|行列)", category_test_string, re.IGNORECASE):
            category = "array"
        elif re.search("(bpmf|注音)", category_test_string, re.IGNORECASE):
            category = "zhuyin"
        elif re.search("(cj|simplex|cangjie|快倉|亂倉|倉頡|簡易|輕鬆)", category_test_string, re.IGNORECASE):
            category = "cangjie"
        elif re.search("(dayi|大易)", category_test_string, re.IGNORECASE):
            category = "dayi"
        elif re.search("(pin|拼)", category_test_string, re.IGNORECASE):
            category = "pinying"

        content['category'] = category

        # additional headers
        headerpath = f"rawdata/misc/{filename}"
        if os.path.exists(headerpath):
            with open(headerpath, "r") as fp:
                additional = trim(fp.read())
                content['license'] = f"{content['license']}\n\n{additional}"

        # print(content)
        jsondata['datatables'].append(content)

        # splits counter
        if not dbFilename in jsondata['splits']:
            jsondata['splits'][dbFilename] = {}

        for repo in repos:
            list = glob.glob(f"{build_dir}/{repo}/{target}/{dbFilename}*")
            # print(f"{filename}: {len(list)}")
            if not repo in jsondata['splits'][dbFilename]:
                jsondata['splits'][dbFilename][repo] = len(list)

    create_json_file(outputPath, jsondata)

def create_lexicon(outputPath):
    target = "lexicon"
    src_path = f"{base_dir}/{target}"
    db_path = f"{base_dir}/build/queue/{target}"

    jsondata = {
        'version': (datetime.now()).strftime(f'%Y%m%d%H%M%S'),
        'resources': [],
        'splits': {},
    }

    for path in sorted(glob.glob(f"{db_path}/*.csv.db")):
        db_filename = os.path.basename(path)
        filename = db_filename.replace('.db', '')
        txt_path = f"{src_path}/{filename}.txt"

        if not os.path.exists(txt_path):
            print("File not found: {txtPath}")
            continue

        # splitFile(f"{dbPath}/{dbFilename}", f"{repos['github']}/{target}/{dbFilename}", 2048)
        # splitFile(f"{dbPath}/{dbFilename}", f"{repos['gitee']}/{target}/{dbFilename}", 1024)

        reader = open(f"{src_path}/{filename}.txt", 'r')
        template = reader.read()
        template = template.strip()
        reader.close()

        tmp = template.split("\n")
        name = trim(tmp[0].lstrip('#').rstrip('#'))
        tmp = ''

        # sample
        db = sqlite3.connect(path)
        cursor = db.cursor()
        # cursor.execute("SELECT `phrase`, `pinyin` FROM `lexicon`, `pinyin` WHERE `lexicon`.`pinyin_id` = `pinyin`.`rowid` ORDER BY RANDOM() LIMIT 10")
        cursor.execute("SELECT `phrase`, `pinyin` FROM `lexicon` WHERE 1 ORDER BY RANDOM() LIMIT 10")
        result = cursor.fetchall()
        template += "\n\n#### 詞庫範例\n\n```\n"
        for item in result:
            phrase = item[0] or ''
            pinyin = item[1] or ''
            template += f"{phrase}\t{pinyin}\n"
        template += "```\n\n"

        db.close()

        # print(template)
        jsondata['resources'].append({
            'name': name,
            'path': f"{target}/{db_filename}",
            'description': template,
        })

        # splits counter
        if not db_filename in jsondata['splits']:
            jsondata['splits'][db_filename] = {}

        for repo in repos:
            list = glob.glob(f"{build_dir}/{repo}/{target}/{db_filename}*")
            # print(f"{filename}: {len(list)}")
            if not repo in jsondata['splits'][db_filename]:
                jsondata['splits'][db_filename][repo] = len(list)

    create_json_file(outputPath, jsondata)

def main():
    arg_reader = argparse.ArgumentParser(description='Resource files generator')
    arg_reader.add_argument('-c', '--category', required = True, choices=['keyboard', 'lexicon', 'table'], help='Resource category')
    arg_reader.add_argument('-o', '--output', type = str, required = True, help='Output file path')

    args = arg_reader.parse_args()
    # print(args, len(sys.argv))

    match args.category:
        case 'keyboard':
            create_keyboard(args.output)
        case 'table':
            # patchTableHeaders()
            create_table(args.output)
        case 'lexicon':
            create_lexicon(args.output)

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
