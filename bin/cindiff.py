#!/usr/bin/env uv run
#
# Identifying unique characters that appear in the first .cin file but are absent from the second.
#
import argparse
import sys, os
import unicodedata
from collections import defaultdict

def extract_mapping(filename):
    """Returns a dictionary of {char: [codes]} found in the chardef block."""
    # mapping = defaultdict(list)
    chars = set()
    in_chardef = False

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for _line in f:
                # remove comments
                line = _line.split('#')[0]
                # strip whitespace
                line = line.strip()
                if not line:
                    continue
                if line == "%chardef begin":
                    in_chardef = True
                    continue
                if line == "%chardef end":
                    in_chardef = False
                    continue

                if in_chardef:
                    parts = line.split()
                    if len(parts) >= 2:
                        # parts[0] is the code (e.g., 'ab')
                        # parts[1] is the character (e.g., '的')
                        chars.add(parts[1])
                        # code, char = parts[0], parts[1]
                        # if code not in mapping[char]:
                        #     mapping[char].append(code)
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        sys.exit(1)
    # return mapping
    return chars


def get_cjk_block(char_str):
    """Identifies CJK blocks safely, handling symbols and long strings."""
    if not char_str:
        return "Empty"

    first_char = char_str[0]
    cp = ord(first_char)

    # If the string is longer than 1, it's likely a symbol/phrase
    if len(char_str) > 1:
        return "Special Symbols / Phrases"

    # CJK Range Logic
    if 0x4E00 <= cp <= 0x9FFF: return "CJK Unified Ideographs"
    if 0x3400 <= cp <= 0x4DBF: return "CJK Extension A"
    if 0x20000 <= cp <= 0x2A6DF: return "CJK Extension B"
    if 0x2A700 <= cp <= 0x2B73F: return "CJK Extension C"
    if 0x2B740 <= cp <= 0x2B81F: return "CJK Extension D"
    if 0x2B820 <= cp <= 0x2CEAF: return "CJK Extension E"
    if 0x2CEB0 <= cp <= 0x2EBEF: return "CJK Extension F"
    if 0xF900 <= cp <= 0xFAFF: return "CJK Compatibility Ideographs"
    return "Other / Miscellaneous"


def chardef_diff(file1, file2, output_file):
    map1 = extract_mapping(file1)
    map2 = extract_mapping(file2)

    # Characters in File 1 that are missing from File 2
    # missing_chars = set(map1.keys()) - set(map2.keys())
    missing_chars = map1 - map2

    if not missing_chars:
        print("No missing characters found in the second file.")
        return

    # Grouping
    grouped = defaultdict(list)
    for char in sorted(missing_chars):
        block = get_cjk_block(char)
        # block = "misc"
        # Store as (character, original_codes_from_file1)
        # grouped[block].append((char, map1[char]))
        grouped[block].append(char)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Missing Characters Report\n")
        f.write(f"Source: {file1}\nTarget: {file2}\n")
        f.write(f"Total Missing: {len(missing_chars)}\n")
        f.write("="*60 + "\n\n")

        # for block, items in sorted(grouped.items()):
        #     f.write(f"## {block}\n")
        #     f.write(f"{'Char':<5} | {'Source Codes (File 1)':<20}\n")
        #     f.write("-" * 30 + "\n")
        #     for char, codes in items:
        #         code_str = ", ".join(codes)
        #         f.write(f"{char:<5} | {code_str:<20}\n")
        #     f.write("\n")

        for block in sorted(grouped.keys()):
            f.write(f"## {block} ({len(grouped[block])} chars)\n")
            chars = grouped[block]
            f.write("\n".join(chars) + "\n\n")

    print(f"Results saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description="cin diff tool"
    )
    parser.add_argument(
        "-p",
        "--primary-file",
        help="The primary file path"
    )
    parser.add_argument(
        "-s",
        "--secondary-file",
        help="The secondary file path"
    )
    parser.add_argument(
        "-o",
        "--output-file",
        help="The output file path"
    )

    args = parser.parse_args()
    chardef_diff(args.primary_file, args.secondary_file, args.output_file)


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
