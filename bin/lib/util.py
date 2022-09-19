#!/usr/bin/env python
#
# version: 1.0.0
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

def prompt(q):
    try:
        a = input(q + ' ')
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
    try:
        code = eval('Colors.' + fg)
        return code + text + eval('Colors.reset')
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

def trim(str, needle = None):
    # _str = str(str)
    _str = str
    if needle:
        _str = re.sub(r'(?m)^ *' + needle + '.*\n?', '', _str)
    return _str.strip()

def stripAccents(str):
    return ''.join(c for c in unicodedata.normalize('NFD', str) if unicodedata.category(c) != 'Mn')

def dir(path):
    return os.path.dirname(os.path.realpath(path))

def chunks(reader, size = 10000):
    chunk = []
    for i, line in enumerate(reader):
        if (i % size == 0 and i > 0):
            yield chunk
            # del chunk[:]
            chunk = []
        chunk.append(line)
    yield chunk

def getOne(cursor, query, args = None):
    if args == None:
        cursor.execute(query)
    else:
        cursor.execute(query, args)
    # result = cursor.fetchone()
    return next(cursor, [None])[0]
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
