#!/usr/bin/env python
#
# version: 0.0.5
# autor: Ethan Liu
#
# all about emoji
# since all we need for emoji are only a few files
# using the whole repo is kinda heavy, download individual file instead
#
# refs:
# https://github.com/unicode-org/cldr-json
# https://carpedm20.github.io/emoji/docs

import argparse
import sys, os, importlib
import urllib3, shutil
import re, json, sqlite3
from emoji import is_emoji

uu = importlib.import_module("lib.util")

# import requests
# import ssl
# import certifi
# import codecs
# REPO_PATH = os.path.realpath(os.path.dirname(__file__) + '/../rawdata/cldr-json/cldr-json')

COMMON_WORDS_LIST = ['skin tone', '皮膚', '肤色']

PACKAGES_LIST = [
    'cldr-annotations-derived-full/annotationsDerived/{}/annotations.json',
    'cldr-annotations-full/annotations/{}/annotations.json',
]

LANGS = ['en', 'zh-Hant', 'zh']

# REF: https://home.unicode.org/emoji/emoji-frequency/
# top = "😂❤️🤣👍😭🙏😘🥰😍😊🎉😁💕🥺😅🔥☺️🤦♥️🤷🙄😆🤗😉🎂🤔👏🙂😳🥳😎👌💜😔💪✨💖👀😋😏😢👉💗😩💯🌹💞🎈💙😃😡💐😜🙈🤞😄🤤🙌🤪❣️😀💋💀👇💔😌💓🤩🙃😬😱😴🤭😐🌞😒😇🌸😈🎶✌️🎊🥵😞💚☀️🖤💰😚👑🎁💥🙋☹️😑🥴👈💩✅"
RANKING = [
    '😂❤️',
    '😍🤣',
    '😊🙏💕😭😘',
    '👍😅👏😁♥️🔥💔💖💙😢🤔😆🙄💪😉☺️👌🤗',
    '💜😔😎😇🌹🤦🎉‼️💞✌️✨🤷😱😌🌸🙌😋💗💚😏💛🙂💓🤩😄😀🖤😃💯🙈👇🎶😒🤭❣️',
    '❗😜💋👀😪😑💥🙋😞😩😡🤪👊☀️😥🤤👉💃😳✋😚😝😴🌟😬🙃🍀🌷😻😓⭐✅🌈😈🤘',
    '💦✔️😣🏃💐☹️🎊💘😠☝️😕🌺🎂🌻😐🖕💝🙊😹🗣️💫💀👑🎵🤞😛🔴😤🌼😫⚽🤙☕🏆🧡🎁⚡🌞🎈❌✊👋😲🌿🤫👈😮🙆🍻🍃🐶💁😰🤨😶🤝🚶💰🍓💢',
    '🇺🇸🤟🙁🚨💨🤬✈️🎀🍺🤓😙💟🌱😖👶▶️➡️❓💎💸⬇️😨🌚🦋😷🕺⚠️🙅😟😵👎🤲🤠🤧📌🔵💅🧐🐾🍒😗🤑🚀🌊🤯🐷☎️💧😯💆👆🎤🙇🍑❄️🌴🇧🇷💣🐸💌📍🥀🤢👅💡💩⁉️👐📸👻🤐🤮🎼✍️🚩🍎🍊👼💍📣🥂⤵️📱☔🌙',
    '🍾🎧🍁⭕🏀☠️⚫🖐️😧🎯📲☘️👁️🍷👄🐟🍰💤🕊️📺💭🐱🐝🇲🇽🧚🔝📢📷🐕🎸🔫🤚🍭🍆💉🌎😦🌀👿☑️🎥🌧️👽🍋🤒🤡🍫📚🏁🤕🦄🍅🚗🚫💵⚾🔪🔔♨️🌳🔊🍬💏🍼🍜🐼🙉🐈🐻🤸🌝👸🍕🍌🍦⚪👩😿🍂📞⏰🔞🌍🌠🙀▪️☁️👹🍉🐥🌶️1️⃣🌵🇮🇳👧🍄👮💮🐰🔷🌾🔹🇹🇷🥇🇮🇹',
    '🍪🇦🇷🛑🐍🎓🇨🇦🍏🦁😽🚬🍖🍴🆘🤜🍿🍔📝🇯🇵🍮🍇2️⃣🏠🤰🐣🐒👦🍩🍣🤛👯🏳️‍🌈♠️🌲🐴🍛🎆💑🍞🍯☄️😸🍚🎬🎙️🇨🇴🐳🦀🥃🔸💊🐎🍹♦️🔮👨🍸🌏👴🧢🐽🐔🎻⬆️✂️👫👣🐯🎮🍵🐦🇬🇧〰️👭🐬🍟👙✖️📩👵🍨🇫🇷🐖✝️♻️🥊🦅💬🇨🇱🐢🔰🔶🎗️💄👠🥕➖🐺📖🍍🌃✴️🌌🐓👂🍤🐐🔻💻🦐🇩🇪🌛↘️✏️🧘🥁🏖️⚜️❕🅰️🚴💠㊗️🐙♣️🍡⏩🎨🐠🇰🇷🍗🚮▫️🌪️😼👤🏊🌽🎩🇪🇸🎹🍈◀️↔️🏡🇵🇰🎇🥩🐞3️⃣⬅️🌐↗️🍽️🧀🥦🐜⚔️',
    '😺🥞🏄🔨🏝️🔆👥👓🥒🏈🇵🇭🏋️0️⃣🚘🦖🌕🎭👾🍳🏵️🍧🔗🕋☃️🌅🤴🖖🐊🐘🌤️🥑🥚⛈️🐵🔜🍶🐄🇻🇪🐮🦈🚲⛔🕯️➕🔺💇🧠📻🥤🍝🍥💴🌬️🥓🙍⚓👰🐂📽️🏅⛅🇦🇪🇵🇪🧜📮⛳🔽🚂🏌️🐇🏍️🎲🥛🎣👱🎏🕷️🦍🔘🐅🏇🔐🏩👺🅱️🚙🐧⚖️🎃🌄🎾🐚🎺❇️🎫⌚🌋💒👳❎👟👃🛌🚓⏬📈⛄⏱️😾🛫🤱🍐☮️🚃⏳🌜📹🐛👔👗🐌🎱🌰🌮🕵️🔅✉️🇪🇬🚑📦🤥🔄🤳💲🎋🗓️🤖🥔🆗🔑🇨🇳🐤4️⃣🐑➰👩‍🎓☂️🇦🇹🦆🚌💿🏥🐋🚒🏐🇪🇨🥐🎷🗽🗡️🏏🐭🙎🌑🚔🇮🇩🚿🥝🕌🐀🛡️🔒✳️🕶️👩‍❤️‍💋‍👩🎟️🐉🔱🔎🇦🇺⚰️🐩🦑🧟🆕🦊👕🏹🇩🇿👬🍱📰🥋🚤🏰5️⃣🦉🚢🌨️📆🗝️🎌🧔💳🇺🇾🥗☯️⚙️💶⛩️🗻✒️🇺🇲🇵🇹🍠',
]

def updateResources(basedir):
    baseurl = 'https://github.com/unicode-org/cldr-json/raw/main/cldr-json'
    pool = urllib3.PoolManager()

    for package in PACKAGES_LIST:
        for lang in LANGS:
            url = f"{baseurl}/{package.format(lang)}"
            path = f"{basedir}/{package.format(lang).replace('/', '_')}"

            print(f"Download: {path}")
            with pool.request('GET', url, preload_content=False) as res, open(path, 'wb') as f:
                shutil.copyfileobj(res, f)

            res.release_conn()
    print("Update finished")

def charToLongHex(emoji):
    codes = emoji.encode('unicode-escape').decode('ascii')
    codes = list(filter(None, re.split(r'\\U|\\x', codes, flags=re.IGNORECASE)))
    # print(emoji, codes, path),

    for index, code in enumerate(codes):
        try:
            v = int(code, 16)
        except ValueError:
            # print("Ignore annotation: ", emoji, codes)
            # continue
            # break
            return None

        v = f"{v:08x}"
        codes[index] = v

    codes = ' '.join(codes).upper()
    return codes


def parse(cursor, path):
    file = open(path, 'r')
    data = json.load(file)
    file.close()

    # version = data['annotationsDerived']['identity']['version']['_cldrVersion']
    # cursor.execute("INSERT INTO info VALUES (?, ?)", ("version", version))

    node = None

    if 'annotationsDerived' in data:
        node = data['annotationsDerived']['annotations']
    elif 'annotations' in data:
        node = data['annotations']['annotations']
    else:
        print("node not found: " + path)
        return

    cursor.execute("BEGIN TRANSACTION")

    for emoji in node:
        codes = charToLongHex(emoji)

        if codes == None:
            # print(f"Ignore None Char: {emoji}")
            continue

        if not is_emoji(emoji):
            # simple check against json resource
            if not codes.startswith('0001'):
                # print(f"Ignore Reg Char: {emoji} => {codes}")
                continue
            print(f"New emoji: {emoji} => {codes}")

        # chardef
        cursor.execute("INSERT OR IGNORE INTO chardef (char) VALUES (:char)", {'char': codes})
        chardefId = uu.getOne(cursor, "SELECT rowid FROM chardef WHERE char = :char LIMIT 1", {'char': codes})

        # a quick but unsafe check but since prefix is all we need here
        if not 'default' in node[emoji]:
            # print("emoji: {} has no keywords".format(emoji))
            continue

        keywords = node[emoji]['default']
        for keyword in keywords:
            if any(words in keyword for words in COMMON_WORDS_LIST):
                continue

            # keydef
            cursor.execute("INSERT OR IGNORE INTO keydef (key) VALUES (:key)", {'key': keyword})
            keydefId = uu.getOne(cursor, "SELECT rowid FROM keydef WHERE key = :key LIMIT 1", {'key': keyword})

            # entry pivot
            cursor.execute("INSERT OR IGNORE INTO entry (keydef_id, chardef_id) VALUES (:kid, :cid)", {'kid': keydefId, 'cid': chardefId})

    cursor.execute("COMMIT TRANSACTION")

def performImport(repoPath, dbPath):
    if os.path.isfile(dbPath):
        os.remove(dbPath)

    db = sqlite3.connect(dbPath)
    cursor = db.cursor()

    cursor.execute("CREATE TABLE info (`name` CHAR(255) UNIQUE NOT NULL, `value` CHAR(255) default '')")
    cursor.execute("CREATE TABLE keydef (`key` CHAR(255) UNIQUE NOT NULL)")
    cursor.execute("CREATE TABLE chardef (`char` CHAR(255) UNIQUE NOT NULL)")
    cursor.execute("CREATE TABLE entry (`keydef_id` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL, UNIQUE(`keydef_id`, `chardef_id`) ON CONFLICT IGNORE)")

    for package in PACKAGES_LIST:
        for lang in LANGS:
            # path = f"{args.repo}/{package}".format(lang)
            path = f"{repoPath}/{package.format(lang).replace('/', '_')}"
            # print(path)
            if not os.path.isfile(path):
                print(f"Path not found: {path}")
                continue
            parse(cursor, path)

    db.commit()

    # index
    cursor.execute('vacuum')
    # cursor.execute("CREATE UNIQUE INDEX info_index ON info (name)")
    # cursor.execute("CREATE UNIQUE INDEX keydef_index ON keydef (key)")
    # cursor.execute("CREATE UNIQUE INDEX chardef_index ON chardef (char)")
    # cursor.execute("CREATE INDEX entry_index ON entry (keydef_id, chardef_id)")

    cursor.execute("SELECT COUNT(*) FROM chardef")
    characterCounter = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM keydef")
    keywordsCounter = cursor.fetchone()[0]

    db.close()

    print(f"\nOutput: {dbPath}")
    print(f"Counter: chardef: {characterCounter}, keydef: {keywordsCounter}")

def applyRanking(dbPath):
    db = sqlite3.connect(dbPath)
    cursor = db.cursor()

    columns = [i[1] for i in cursor.execute("PRAGMA table_info(`chardef`)")]
    if 'weight' not in columns:
        print('alter weight column')
        cursor.execute("ALTER TABLE chardef ADD `weight` INTEGER DEFAULT 0")

    for index, items in enumerate(reversed(RANKING)):
        weight = 10000 + (100 * index)
        # print(weight, items)
        for item in items[::-1]:
            weight += 1
            code = charToLongHex(item)
            # print(f"{item} {weight} ", end = ' \n'),
            cursor.execute("UPDATE `chardef` SET weight = :weight WHERE char = :code", {'code': code, 'weight': weight})

    db.commit()

    print(f"\nTop Ranking\n===========")
    cursor.execute("SELECT char FROM `chardef` WHERE weight > 0 ORDER BY weight DESC")
    result = cursor.fetchall()
    for item in result:
        emoji = emojilized(item[0])
        print(emoji, end = ' '),
    print('')

    db.close()
    # print("--end")

def emojilized(hexString):
    codes = r'\U' + r'\U'.join(hexString.split(' '))
    codes = codes.encode('utf8').decode('unicode-escape')
    return codes

def test(phrase, dbPath):
    if not os.path.isfile(dbPath):
        sys.exit("File not found")

    db = sqlite3.connect(dbPath)
    cursor = db.cursor()
    # prefix = "EXPLAIN QUERY PLAN "
    prefix = ""

    if phrase == 'emoji':
        cursor.execute(prefix + "SELECT * FROM chardef WHERE rowid In (SELECT rowid FROM chardef ORDER BY RANDOM() LIMIT 100)")
        result = cursor.fetchall()

        if not result:
            return

        for item in result:
            emoji = emojilized(item[0])
            print(emoji, end = ' '),
        print('')

    else:
        # cursor.execute("SELECT * FROM keydef WHERE rowid IN (SELECT rowid FROM keydef ORDER BY RANDOM() LIMIT 10)")
        # cursor.execute("SELECT * FROM keydef WHERE key LIKE :phrase", {'phrase': '%' + phrase + '%'})
        cursor.execute(prefix + "SELECT DISTINCT chardef.char, keydef.key FROM keydef, chardef, entry WHERE 1 AND  (keydef.key LIKE ? OR keydef.key LIKE ? OR keydef.key LIKE ? OR keydef.key LIKE ?) AND keydef.ROWID = entry.keydef_id AND chardef.ROWID = entry.chardef_id ", [phrase, f'% {phrase} %', f'%{phrase} %', f'% {phrase}%'])

        result = cursor.fetchall()

        if not result:
            print("No result for phrase: ", phrase)
            return

        if prefix:
            print(result)
        else:
            for item in result:
                print(f"{emojilized(item[0])}\t{item[1]}")

    db.close()
    # print("\nEnd of test")


def main():
    argParser = argparse.ArgumentParser(description='emoji.db Utility')
    argParser.add_argument('--update', action=argparse.BooleanOptionalAction, help='Update emoji cldr json files')
    argParser.add_argument('--run', action=argparse.BooleanOptionalAction, help='Run import')
    argParser.add_argument('-test', type = str, help='Test keyword')
    argParser.add_argument('-d', '--dir', type = str, help='The directory path of cldr-json files')
    argParser.add_argument('-o', '--output', type = str, help='The file path of emoji.db')

    args = argParser.parse_args()
    # print(args, len(sys.argv))
    # sys.exit(0)

    # if len(sys.argv) < 2:
    #     argParser.print_usage()
    #     sys.exit(0)

    if args.update:
        if not args.dir or not os.path.exists(args.dir):
            print(f"Directory (rawdata/emoji) not found: {args.dir}")
            sys.exit(0)
        updateResources(args.dir)
        sys.exit(0)

    if args.test:
        if not args.output or not os.path.isfile(args.output):
            print(f"File (emoji.db) not found or missing: {args.output}")
            sys.exit(0)
        test(args.test, args.output)
        sys.exit(0)

    if args.run:
        if not args.dir or not os.path.exists(args.dir):
            print(f"Directory (rawdata/emoji) not found: {args.dir}")
            sys.exit(0)
        performImport(args.dir, args.output)
        applyRanking(args.output)

    sys.exit(0)

if __name__ == "__main__":
    main()
