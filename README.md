# About the app

Frankie/OkidoKey is an input method kit for iOS.

It includes an in-app keyboard with a plain text editor and keyboard extension for system-wide usage. And auto-copy Clipboard for typing without creating or open a document.

https://itunes.apple.com/us/app/okidokey/id945116579?ls=1&mt=8

# About this repo

This repo contains:  

charset - Keyboard layouts configs of Frankie and OkidoKey  
db - Pre-compiled SQLite database for Frankie and OkidoKey  
lexicon - Chinese phrased or idioms in csv format  
table - Input method data tables in cin format  

## Charset format

Each .charset.json must have `name`, `charsets` properties.

The `name` property must be unique in the whole collections.  `charsets` can have multiple strings, each string presents one row of the custom keyboard, it's best to keep in 3 to 4 rows per charset.

Optional properties:

`description`: description for the charset  
`flicks`: flick keys for this charset  
`keynameType`: currently, the only accepted value is `label`, which means the key label can be used as keys for `keyname`, for example `[1:abc]` means when key `1` pressed, it means either `a`, `b` or `c`. 

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

Each key format is wrapping by `[]` and use `:` as the separator.  For example `[1:ㄅ]` represent a key with character `1` and label `ㄅ`, if the character and label are the same, you may ignore the label, i.e. `[A]`. The character must be 1 character only, but the label has no length limit, however, less then 3 characters are recommended.

If there is a `*` followed by the character, then the key will display as a function key, but it still works as a regular key.

If the `keynameType` is the label, and when the character should be recognized as `keyname`, then it must be the character, label pairs, i.e. `[ˇ:ˇ]` otherwise it might be recognized as a regular symbol.

Charset separates into 3 categories:

The name has `-pad` suffix: regular layout for iPad, without tab, capslock keys in general  
The name has `-fullsize` suffix: full-size keyboard layout brought by iPad Pro 12.9  
The name has `-choco` suffix: telephone keypad layout (chocolate), every key in the keyboard is the same size  
The name without any suffix: regular layout for iPhone  

### Reserved keys

A few reserved combinations represent special keys.

- `[capslock]` — caps lock key
- `[del]` — backspace key
- `[dismiss]` — dismiss keyboard for iPad
- `[dummy]` — Spacing between keys, [dummy] or [dummy:1] for one key width, [dummy:2] for half key width, only 1 or 2 is valid.
- `[esc]` - escape key
- `[globe]` — switch to system keyboard
- `[next]` — switch to next charset in OkidoKey.app keyboards
- `[return]` — return key
- `[shift]` — shift key
- `[space]` — space key
- `[tab]` — tab key

## Build

Just use make command, check makefile for the details

