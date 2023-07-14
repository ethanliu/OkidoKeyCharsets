#!/usr/bin/env python
#
# version: 0.1.0
# autor: Ethan Liu
#
# convert table from lime (csv) to cin format with extra header information
#

from datetime import datetime
from tqdm import tqdm
import argparse
import csv
import importlib
import sys, os

uu = importlib.import_module("lib.util")

consoleBufferSize = -1000
# first column for keydef, second column for chardef
column = [0, 1]
chardefBeginBlock = f"%chardef begin\n"
chardefEndBlock = f"%chardef end"

def parser(path, outputPath, headerPath, delimiter = '\t'):
    today = datetime.now()

    description = "# build: {}\n".format(today.strftime(f'%Y/%m/%d %H:%M:%S'))
    header = ""
    contents = ""

    if headerPath == '':
        contents = ['%ename', '%cname', '%selkey', '%keyname begin', '%keyname end']
        header += '\n'.join(contents) + '\n'
    else:
        with open(headerPath) as headerFile:
            for row in headerFile:
                if row.startswith("#"):
                    description += f"{row}"
                else:
                    header += f"{row}"

    # begin

    with open(path) as fp:
        reader = csv.reader(fp, delimiter = delimiter)
        for rows in uu.chunks(reader, 100000):
            for row in tqdm(rows, unit = 'MB', unit_scale = True, ascii = True, desc = f"{path} Chunk[]"):
                if consoleBufferSize > 0 and len(contents) > consoleBufferSize:
                    break
                if not row:
                    # print(f"skip empty: {row}")
                    if not contents:
                        # very first newline
                        contents += chardefBeginBlock
                    continue

                if row[0].startswith("#"):
                    # tmpFile.writelines(f"{' '.join(row)}\n")
                    if not contents:
                        description += f"{' '.join(row)}\n"
                    else:
                        contents += f"{' '.join(row)}\n"
                    continue

                keydef = ""
                chardef = ""

                for index, i in enumerate(column):
                    if (len(row) < 2):
                        continue
                    match i:
                        case 0:
                            keydef = uu.trim(row[index])
                        case 1:
                            items = uu.trim(row[index]).split("#")
                            chardef = items[0].strip()

                if keydef == '' or chardef == '':
                    continue

                contents += f"{keydef}\t{chardef}\n"

    with open(outputPath, 'w') as fp:
        fp.write(description)
        fp.write(f"#\n")
        fp.write(header)
        fp.write(contents)
        fp.write(chardefEndBlock)
        fp.close()

def main():
    argParser = argparse.ArgumentParser(description='Convert CIN table from Lime table')
    argParser.add_argument('-i', '--input', required = True, help='Input file path')
    argParser.add_argument('-o', '--output', required = True, help='Output file path')
    argParser.add_argument('-x', '--header', required = True, help='CIN table header')
    argParser.add_argument('-d', '--delimiter', default='\t', help='Delimiter')

    args = argParser.parse_args()
    # print(args)

    if not os.path.exists(args.input):
        sys.exit(f"File not found: {args.input}")

    if not os.path.exists(args.header):
        sys.exit(f"File not found: {args.header}")

    parser(args.input, args.output, args.header, args.delimiter)


if __name__ == "__main__":
    main()
