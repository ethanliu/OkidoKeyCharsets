#!/usr/bin/env uv run
# OkidoKey/Frankie resources generator

import argparse
import sys
import os
import glob
import re
import sqlite3
import json
from datetime import datetime
from lib.cintable import CinTable
from lib.util import trim, parent_dir, trim, color

# uu = importlib.import_module("lib.util")
base_dir = parent_dir(__file__, 1)
build_dir = f"{base_dir}/build"
repos = ["github", "gitlab"]

def load_json_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_json_file(path, content):
    print(color(f"{os.path.basename(path)} created.", fg = 'cyan'))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, separators=(',', ':'))

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


#
# Transform flick data from KeyMapping to direction map.
# from "q": [["1", "一"], ["2", "二"]]
# to q: [[{"down": "1", "up": "2"}], [{"down": "一", "up": "二"}]]
#
def extract_flicks_by_source(source_dict):
    processed = {}
    for f_key, directions_arr in source_dict.items():
        halfwidth_dirs = {}
        fullwidth_dirs = {}

        # Index 0 -> down directional block
        if len(directions_arr) > 0 and isinstance(directions_arr[0], list) and directions_arr[0]:
            items = directions_arr[0]
            halfwidth_dirs["down"] = str(items[0])
            fullwidth_dirs["down"] = str(items[1]) if len(items) > 1 else str(items[0])

        # Index 1 -> up directional block
        if len(directions_arr) > 1 and isinstance(directions_arr[1], list) and directions_arr[1]:
            items = directions_arr[1]
            halfwidth_dirs["up"] = str(items[0])
            fullwidth_dirs["up"] = str(items[1]) if len(items) > 1 else str(items[0])

        # res = {}
        # if standard_dirs:
        #     res["standard"] = standard_dirs
        # if fullwidth_dirs:
        #     res["fullwidth"] = fullwidth_dirs
        res = []
        res.append(halfwidth_dirs if halfwidth_dirs else [])
        res.append(fullwidth_dirs if fullwidth_dirs else [])

        if res:
            processed[f_key.lower()] = res
    return processed

#
# Parse keys from row_str
# Mapping popups and flicks form KeyMapping
# Override inline popups if any
#
def parse_charset_row(row_str, layout_popups, processed_flicks, layout_item, layout_name):
    charset_regex = r"\[(.*?[^:])(?::((?:[^\]]*)))?\]"
    row_str = row_str.replace("[:]", "[colon]").replace("[::]", "[colon]").replace("[:::]", "[colon]")
    matches = re.findall(charset_regex, row_str)

    layout_lower = layout_name.lower()
    supports_flicks = any(x in layout_lower for x in ["flick", "pad", "fullsize"])

    row_keys = []
    for match in matches:
        raw_key = match[0].strip()
        radical_label = match[1].strip() if match[1] else ""

        is_alternative_key = False
        if len(raw_key) > 1 and raw_key.endswith('*'):
            is_alternative_key = True
            raw_key = raw_key[:-1]

        lookup_key = raw_key.lower()
        if raw_key == "colon":
            raw_key = ":"
            lookup_key = ":"
        elif raw_key == "dummy" and not radical_label:
            radical_label = "1"

        # is_input_method_radical = is_radical_override or (layout_item.get("keynameType") == "label" and len(radical_label) > 0)

        # Handle Flicks Normalization
        # flicks_payload = None
        # key_flicks = None
        key_flicks = []
        if supports_flicks:
            inline_flicks = layout_item.get("flicks", {}).get(lookup_key)
            if inline_flicks is not None:
                # key_flicks = {
                #     "standard": inline_flicks,
                # }
                key_flicks = [inline_flicks]
            else:
                key_flicks = processed_flicks.get(lookup_key, None)

        key_popups = inline_popups if (inline_popups := layout_item.get("popups", {}).get(lookup_key)) is not None else layout_popups.get(lookup_key, None)

        # row_keys.append({
        #     "key": raw_key,
        #     "radicalLabel": radical_label,
        #     "isAlternativeKey": is_alternative_key,
        #     "popups": key_popups,
        #     "flicks": key_flicks,
        # })
        row_keys.append([
            raw_key,
            radical_label,
            is_alternative_key,
            key_popups,
            key_flicks,
        ])
    return row_keys

def parse_function_key_row(row_str):
    fnkeys = ["capslock", "del", "dismiss", "esc", "globe", "next", "shift", "tab"]
    features = []
    for fnkey in fnkeys:
        if f"[{fnkey}]" in row_str:
            features.append(fnkey)
    return features

# build hydrated keyboard layouts
def build_keyboard(charset_dir, mapping_path, output_path, default_layout):
    mapping_raw = load_json_file(mapping_path)
    symbols_map = mapping_raw.get("symbol", {})
    numerics_map = mapping_raw.get("numeric", {})
    alphanumerics_map = mapping_raw.get("alphanumeric", {})

    flicks_pad = extract_flicks_by_source(mapping_raw.get("flick", {}))
    flicks_fullsize = extract_flicks_by_source(mapping_raw.get("flick2", {}))

    jsondata = {
        'version': datetime.now().strftime('%Y%m%d%H%M%S'),
        'layouts': {}
    }

    categories = {"bpmf": "bpmf", "symbol": "symbol", "easy": "cangjie"}
    filelist = sorted(glob.glob(os.path.join(charset_dir, "*.charset.json")))

    for path in filelist:

        base_filename = os.path.basename(path).split(".")[0]

        is_default_file = (base_filename == "default")
        if default_layout != is_default_file:
            continue

        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        category = base_filename
        for ck, cv in categories.items():
            if base_filename.startswith(ck):
                category = cv

        for item in data:
            name = item.get('name')
            if not name or name.startswith('_') or 'charsets' not in item or name in jsondata['layouts']:
                continue

            charsets = item.get('charsets', [])
            first_row = charsets[0] if len(charsets) > 0 else ""
            is_numeric_row = len(re.findall(r"\[[0-9]", first_row)) >= 9

            if is_numeric_row:
                base_popups = numerics_map
                base_flicks = flicks_fullsize
            elif "symbol" in name or category == "symbol":
                base_popups = symbols_map
                base_flicks = flicks_pad
            else:
                base_popups = alphanumerics_map
                base_flicks = flicks_pad

            layout_popups = {k.lower(): [k.lower()] + v for k, v in base_popups.items()}

            switched_keys = {}
            if "azerty" in name:
                switched_keys = {"q": "a", "w": "z"}
            elif "dvorak" in name:
                switched_keys = {"q": "'", "w": ",", "e": ".", "r": "p", "t": "y", "y": "f", "u": "g", "i": "c", "o": "r", "p": "l"}
            elif "qwertz" in name:
                switched_keys = {"y": "z"}
            elif "colemak" in name:
                switched_keys = {"e": "f", "r": "p", "t": "g", "y": "j", "u": "l", "i": "u", "o": "y"}

            if switched_keys:
                cached_popups = dict(layout_popups)
                new_keys = set(switched_keys.values())
                for qwerty_key, new_key in switched_keys.items():
                    if qwerty_key in cached_popups:
                        layout_popups[new_key] = cached_popups[qwerty_key]
                    if qwerty_key not in new_keys:
                        layout_popups.pop(qwerty_key, None)

            structured_rows = []
            function_keys = []
            for row_str in charsets:
                parsed_row = parse_charset_row(row_str, layout_popups, base_flicks, item, name)
                structured_rows.append(parsed_row)
                parsed_func_row = parse_function_key_row(row_str)
                function_keys = list({*function_keys, *parsed_func_row})

            jsondata['layouts'][name] = {
                'description': item.get('description') or '',
                'category': category,
                'keynameType': item.get('keynameType') or '',
                'functionKeys': function_keys,
                'rows': structured_rows
            }

    create_json_file(output_path, jsondata)

def build_table(outputPath):
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
        db_filename = os.path.basename(path)
        filename = db_filename.replace('.db', '')

        # splitFile(f"{dbPath}/{dbFilename}", f"{repos['github']}/{target}/{dbFilename}", 2048)
        # splitFile(f"{dbPath}/{dbFilename}", f"{repos['gitee']}/{target}/{dbFilename}", 1024)

        cin = CinTable(f"{src_path}/{filename}", [])
        content = {
            'ename': cin.meta.get('ename') or '',
            'cname': cin.meta.get('cname') or '',
            'name': cin.meta.get('name') or '',
            'path': f"{target}/{db_filename}",
            # 'src': f"{target}/{filename}",
            'license': cin.description,
            'category': '',
        }

        category = "misc"
        category_test_string = f"{content['ename']} {content['cname']} {content['name']} {db_filename}"
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
        headerpath = f"{base_dir}/misc/{filename}"
        if os.path.exists(headerpath):
            # print(headerpath)
            with open(headerpath, "r") as fp:
                additional = trim(fp.read())
                content['license'] = f"{content['license']}\n\n{additional}"

        # print(content)
        jsondata['datatables'].append(content)

        # splits counter
        if not db_filename in jsondata['splits']:
            jsondata['splits'][db_filename] = {}

        for repo in repos:
            list = glob.glob(f"{build_dir}/{repo}/{target}/{db_filename}*")
            # print(f"{filename}: {len(list)}")
            if not repo in jsondata['splits'][db_filename]:
                jsondata['splits'][db_filename][repo] = len(list)

    create_json_file(outputPath, jsondata)

def build_lexicon(outputPath):
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
            print(f"File not found: {txt_path}")
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
    arg_reader.add_argument('-c', '--category', required = True, choices=['default_keyboard', 'keyboard', 'lexicon', 'table'], help='Resource category')
    arg_reader.add_argument('-o', '--output', type = str, required = True, help='Output file path')

    args = arg_reader.parse_args()
    # print(args, len(sys.argv))

    match args.category:
        case 'keyboard':
            build_keyboard(
                output_path=args.output,
                charset_dir=f"{base_dir}/charset",
                mapping_path=f"{base_dir}/KeyMapping.json",
                default_layout=False
            )
        case 'default_keyboard':
            build_keyboard(
                output_path=args.output,
                charset_dir=f"{base_dir}/charset",
                mapping_path=f"{base_dir}/KeyMapping.json",
                default_layout=True
            )
        case 'table':
            # patchTableHeaders()
            build_table(args.output)
        case 'lexicon':
            build_lexicon(args.output)

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
