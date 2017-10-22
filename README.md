# OkidoKeyCharsets

Collections of Charsets for OkidoKey.app v2 series.

OkidoKey.app is the next generation of zhim! extended for iOS8+ which supports system wide custom keyboards.

OkidoKeyCharsets is a collection of charsets for OkidoKey.app custom keyboards.

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

Each key syntax is wrapper by `[]` and use `:` as separator.  For example `[1:ㄅ]` represent a key with character `1` and label `ㄅ`, if the character and label is the same, you may ignore the label, i.e. `[A]`. The character must be 1 character only, but the label has no length limit.

A few reserved combinations represent special keys.

- `[del]` — backspace key
- `[globe]` — switch to system keyboard
- `[next]` — switch to next charset in OkidoKey.app keyboards
- `[return]` — return key
- `[shift]` — shift key
- `[space]` — space key
- `[dismiss]` — dismiss keyboard for iPad
- `[dummy]` — Spacing between keys, [dummy] or [dummy:1] for one key width, [dummy:2] for half key width, only 1 or 2 is valid.

