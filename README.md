# baker.charsetslist
Collections of Charsets for baker.app

baker.app is the next generation of zhim! extended for iOS8+ which supports system wide custom keyboards.

CharsetsList is a collection of charsets for baker.app  custom keyboards.

Each .charset.json mucst have `name`, `charsets` and an optional `description` properties. The `name` property must be unique in the whole collections.  `charsets` can has multiple strings, each string present one row of custom keyboard, it's best to keep in 3 to 4 rows per charset.

    {
        "name": "bpmf",
        "description": "注音鍵盤",
        "charsets":
        [
            "[1:ㄅ][2:ㄉ][3:ˇ][4:ˋ][5:ㄓ][6:ˊ][7:˙][8:ㄚ][9:ㄞ][0:ㄢ][-:ㄦ]",
            "[Q:ㄆ][W:ㄊ][E:ㄍ][R:ㄐ][T:ㄔ][Y:ㄗ][U:ㄧ][I:ㄛ][O:ㄟ][P:ㄣ]",
            "[A:ㄇ][S:ㄋ][D:ㄎ][F:ㄑ][G:ㄕ][H:ㄘ][J:ㄨ][K:ㄜ][L:ㄠ][;:ㄤ]",
            "[shift][Z:ㄈ][X:ㄌ][C:ㄏ][B:ㄖ][V:ㄒ][N:ㄙ][M:ㄩ][,:ㄝ][.:ㄡ][/:ㄥ][del]",
            "[next][globe][space][return]"
        ]
    }
    
Each key syntax is wrapper by `[]` and use `:` as separator.  For example `[1:ㄅ]` represent a key with character `1` and label `ㄅ`, if the character and label is the same, you may ignore the label, i.e. `[A]`. The character must be 1 character only, but the label has no length limit. 

A rew reserved combinations represent special keys.

- `[del]` — backspace key
- `[globe]` — switch to system keyboard
- `[next]` — switch to next charset in baker.app keyboards
- `[return]` — return key
- `[shift]` — shift key
- `[space]` — space key




