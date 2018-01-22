# OkidoKey Charsets

Collections of Keyboard layouts and cin data table for OkidoKey.app v2 series.

OkidoKey includes in-app keyboard with plain text editor and keyboard extension for system-wide usage. And auto-copy Clipboard for typing without create or open a document.

OkidoKey Charsets is a collection of cin data table and keyboard layouts for OkidoKey.app custom keyboards.

Each .charset.json must have `name`, `charsets` and an optional `description` properties. The `name` property must be unique in the whole collections, and with `-pad` suffix present for iPad.  `charsets` can has multiple strings, each string present one row of custom keyboard, it's best to keep in 3 to 4 rows per charset.

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

OkidoKey app:

https://itunes.apple.com/us/app/okidokey/id945116579?ls=1&mt=8
