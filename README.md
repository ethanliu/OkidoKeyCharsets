# About OkidoKey

OkidoKey is an input method kit for iOS.  
It includes in-app keyboard with plain text editor and keyboard extension for system-wide usage. And auto-copy Clipboard for typing without create or open a document.

https://itunes.apple.com/us/app/okidokey/id945116579?ls=1&mt=8

# About this repo

This repo contains:  
charset - Keyboard layouts configs of OkidoKey.app  
db - Pre-compiled database for OkidoKey.app  
table - Input method data tables in cin format

## Charset format

Each .charset.json must have `name`, `charsets` and an optional `description` properties. The `name` property must be unique in the whole collections.  `charsets` can has multiple strings, each string present one row of custom keyboard, it's best to keep in 3 to 4 rows per charset.

    {
        "name": "bpmf",
        "description": "注音鍵盤",
        "charsets":
        [
            "[1:ㄅ][2:ㄉ][3:ˇ][4:ˋ][5:ㄓ][6:ˊ][7:˙][8:ㄚ][9:ㄞ][0:ㄢ][-:ㄦ]",
            "[Q:ㄆ][W:ㄊ][E:ㄍ][R:ㄐ][T:ㄔ][Y:ㄗ][U:ㄧ][I:ㄛ][O:ㄟ][P:ㄣ]",
            "[A:ㄇ][S:ㄋ][D:ㄎ][F:ㄑ][G:ㄕ][H:ㄘ][J:ㄨ][K:ㄜ][L:ㄠ][;:ㄤ]",
            "[shift][Z:ㄈ][X:ㄌ][C:ㄏ][V:ㄒ][B:ㄖ][N:ㄙ][M:ㄩ][,:ㄝ][.:ㄡ][/:ㄥ][del]",
            "[next][globe][space][return]"
        ]
    }

Each key format is wrapping by `[]` and use `:` as separator.  For example `[1:ㄅ]` represent a key with character `1` and label `ㄅ`, if the character and label is the same, you may ignore the label, i.e. `[A]`. The character must be 1 character only, but the label has no length limit, however it's recommend less then 3 characters.

Charset separates into 3 categories:

name has `-pad` suffix: regular layout for iPad, without tab, capslock keys in general  
name has `-fullsize` suffix: full size keyboard layout brought by iPad Pro 12.9  
name has `-choco` suffix: telephone keypad layout (chocolate), every key in the keyboard is the same size  
name without any suffix: regular layout for iPhone  

### Reserved keys

A few reserved combinations represent special keys.

- `[capslock]` — caps lock key
- `[del]` — backspace key
- `[dismiss]` — dismiss keyboard for iPad
- `[dummy]` — Spacing between keys, [dummy] or [dummy:1] for one key width, [dummy:2] for half key width, only 1 or 2 is valid.
- `[globe]` — switch to system keyboard
- `[next]` — switch to next charset in OkidoKey.app keyboards
- `[return]` — return key
- `[shift]` — shift key
- `[space]` — space key
- `[tab]` — tab key

## Build

    > php bin/make.php
    
    NAME
    	make.php -- OkidoKey Package Tools

    SYNOPSIS
    	make.php [options]
    	make.php -x [level] input.cin > output.cin

    OPTIONS:
    	-k	Generate KeyboardLayouts.json
    	-t	Generate DataTables.json
    	-d	Generate Databases

    	-x[level]	Strip Unicode blocks (BMP, SPUA, CJK-Ext...)
        			level 0: strip all blocks (default)
        			level 1: strip all blocks except CJK-ExtA
        			level 2: strip SPUA blocks
        			level 3: strip CJK-Ext A~D blocks
    

