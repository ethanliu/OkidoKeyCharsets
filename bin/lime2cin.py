#!/usr/bin/env python
#
# version: 0.0.1
# autor: Ethan Liu
#
# convert table from lime (csv) to cin format
# the currenct format of lime seems matched cin format by key:value already
# while lime using value:key previously, if I recall
#

import argparse
import sys, os
import tempfile
import shutil
from datetime import datetime

def parser(path, outputPath, headerPath):
    today = datetime.now()

    tmpFile = tempfile.NamedTemporaryFile(mode = 'w+t', delete = False)
    tmpFile.writelines('# build: {}\n'.format(today.strftime(f'%Y/%m/%d %H:%M:%S')))

    if headerPath == '':
        contents = ['%ename', '%cname', '%selkey', '%keyname begin', '%keyname end']
        tmpFile.writelines('\n'.join(contents) + '\n')
    else:
        with open(headerPath) as headerFile:
            # header = headerFile.readlines()
            # use whatever it offers and replace newline
            contents = [line.rstrip() + '\n' for line in headerFile]
            tmpFile.writelines(contents)

    # print(header)
    if contents[-1].rstrip() != f'%chardef begin':
        tmpFile.writelines([f'%chardef begin\n'])

    file = open(path, 'r')
    # contents = file.readlines()
    # count = 0
    for content in file:
        # count += 1
        if not content.strip():
            continue
        else:
            items = content.split('#')
            content = items[0].rstrip()
            items = content.split("\t")
            keydef = items[0].strip()
            chardef = items[1].strip()
            if keydef == '' or chardef == '':
                continue

            # print(keydef, chardef)
            # TODO: any furture check? duplicate items?
            tmpFile.writelines('{}\t{}\n'.format(keydef, chardef))

        # if (count > 10):
        #     break

    tmpFile.writelines([f'%chardef end'])

    tmpPath = tmpFile.name
    tmpFile.close()

    if outputPath == '':
        os.system("cat " + tmpPath)
    else:
        # just overwrite
        shutil.copy(tmpPath, outputPath)

    os.remove(tmpPath)


def main():
    argParser = argparse.ArgumentParser(description='Convert lime table file to cin format')
    argParser.add_argument('input', default='', help='input file path - lime format')
    argParser.add_argument('-output', '-O', default='', help='output file path - cin format')
    argParser.add_argument('-header', '-H', default='', help='cin table header')

    args = argParser.parse_args()
    # print(args)

    if not os.path.isfile(args.input):
        print("input file not found")
        sys.exit(0)

    if args.header != '' and not os.path.isfile(args.header):
        sys.exit("header file not found")

    # if args.output == '':
    #     print("output to stdin")
    # elif not os.path.isfile(args.output):
    #     print("file exists, overwrite?")

    parser(args.input, args.output, args.header)


if __name__ == "__main__":
    main()
