#!/usr/bin/env python
#
# version: 1.0.1
# autor: Ethan Liu
#
# some common python class, functions, etc.
#
#

import sys
import subprocess
import re
import os
import unicodedata
import string
# from tqdm import tqdm
from itertools import islice

class Colors:
    reset = '\u001b[0m'
    black = '\u001b[30m'
    red = '\u001b[31m'
    green = '\u001b[32m'
    yellow = '\u001b[33m'
    blue = '\u001b[34m'
    magenta = '\u001b[35m'
    cyan = '\u001b[36m'
    white = '\u001b[37m'

    # text = '\u001b[0;37m'
    ok = '\033[94m'
    cancel = '\033[96m'
    success = '\033[92m'
    warning = '\033[93m'
    fail = '\033[91m'

    def f(self):
        return 'xxx'

def prompt(q: str, defaultValue = None):
    suffix = ' '
    typeof = ''
    if defaultValue != None:
        typeof = f"{type(defaultValue)}"
        if defaultValue == True:
            suffix = ' [Y/n] '
        elif defaultValue == False:
            suffix = ' [y/N] '
    try:
        a = input(q + suffix)
        a = trim(a)
        if "bool" in typeof:
            if a.lower() == "y" or a.lower() == "yes":
                return True
            return False
        return a
    except KeyboardInterrupt:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

#  run system command without content
def run(args):
    process = subprocess.run(args, shell = True)
    return process

def call(args):
    process = subprocess.check_call(args, shell = True)
    return process

#  run system command with content
def exec(args):
    # process = subprocess.run(args, stdout=subprocess.PIPE, universal_newlines=True)
    process = subprocess.check_output(args)
    return process

def natsorted(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)

def color(text, fg = None):
    if not fg:
        return text
    try:
        # code = eval('Colors.' + fg)
        code = getattr(Colors, fg)
        return eval(code) + text + eval('Colors.reset')
    except:
        return text

# def color(text, fg = None):
#     def _code(fg):
#         try:
#             code = eval('Colors.' + fg)
#         except:
#             # code = eval('Colors.white')
#             code = None
#         return code

#     return _code(fg) + text + eval('Colors.reset')

def whitespace(text):
    replacement = r"\1 \2"
    pattern1 = r"([\u4e00-\u9fa5\u3040-\u30FF])([a-z0-9@#&;=_\[\(])"
    pattern2 = r"([a-z0-9#!~&;=_\]\,\.\:\?\)])([\u4e00-\u9fa5\u3040-\u30FF])"

    text = re.sub(pattern1, replacement, text, flags=re.UNICODE|re.IGNORECASE)
    text = re.sub(pattern2, replacement, text, flags=re.UNICODE|re.IGNORECASE)
    text = trim(text)
    return text

def trim(str, needle = None, space = False):
    # _str = str(str)
    if not str:
        return ""
    _str = str
    if needle:
        _str = re.sub(r'(?m)^ *' + needle + '.*\n?', '', _str)
    if space:
        pattern1 = r"([\u4e00-\u9fa5\u3040-\u30FF])([a-z0-9@#&;=_\\[\\(])"
        pattern2 = r"([a-z0-9#!~&;=_\],\\.:\\?\\)])([\u4e00-\u9fa5\u3040-\u30FF])"
        _str = re.sub(pattern1, "\\1 \\2", _str, 0,re.MULTILINE | re.IGNORECASE | re.UNICODE)
        _str = re.sub(pattern2, "\\1 \\2", _str, 0,re.MULTILINE | re.IGNORECASE | re.UNICODE)
    return _str.strip()

def strip_accents(text, numeric = False):
    if numeric:
        return text.translate(str.maketrans('', '', string.digits))
    else:
        return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

def dir(path):
    return os.path.dirname(os.path.realpath(path))

def parent_dir(path, level = 1):
    dirs = [os.path.dirname(path)]
    for i in range(level):
        dirs.append(os.path.pardir)
    return os.path.normpath(os.path.join(*dirs))

def total_lines(path):
    total = 0
    with open(path, 'r') as fp:
        total = len(fp.readlines())
    return total

def chunks(reader, size = 100000, max = 0):
    chunk = []
    data = enumerate(reader)
    if max > 0:
        data = islice(data, max)
    for i, line in data:
        if (i % size == 0 and i > 0):
            yield chunk
            # del chunk[:]
            chunk = []
        chunk.append(line)
    yield chunk

# def xtqdm(data, size = 1000, desc = "", max: int = 0):
#     size = max > 0 if max else size
#     for chunk in chunks(data, size, max):
#         # how to yield?
#         yield tqdm(chunk, desc = desc, unit = 'MB', unit_scale = True, ascii = True)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def db_get_all(cursor, query, args = None):
    if args == None:
        res = cursor.execute(query)
    else:
        res = cursor.execute(query, args)
    return res.fetchall()

def db_get_one(cursor, query, args = None):
    if args == None:
        cursor.execute(query)
    else:
        cursor.execute(query, args)
    if not cursor.connection.row_factory:
        return next(cursor, [None])[0]
    else:
        result = cursor.fetchone()
        if not result:
            return None
        # print(result)
        # print(list(result.values())[0])
        return list(result.values())[0]


    # print(result)
    # return result[0]

    # try:
    #     result = result[0]
    # except TypeError:
    #     # print("not array")
    #     result = result
    #     pass
    # else:
    #     result = result
    # return result

def vprint(message: str, verbose = True):
    if not verbose:
        return
    print(message)


def list_flatten(xss):
    return [x for xs in xss for x in xs]

def list_unique(rows):
    return list(dict.fromkeys(filter(None, rows)))

# clean code purpose

def read_file(path):
    with open(path, mode = 'r', encoding = 'utf-8') as fp:
        content = fp.read()
        return content

def write_file(path, contents, mode = 'w'):
    with open(path, mode = mode, encoding = 'utf-8') as fp:
        fp.write(contents)


