## CIN 輸入法表格

CIN 表格為 gcin, xcin, scim 等輸入法引擎使用的資料格式。  
CIN 表格包含輸入法名稱，使用按鍵及字根組合等輸入法相關內容的純文字文件。  
以注音輸入法為例，其內容如下:

```
# 注音輸入法表格
%gen_inp
%ename  Phonetic
%cname  注音
%selkey  123456789
%endkey  3467
%keyname  begin
,  ㄝ
-  ㄦ
0  ㄢ
1  ㄅ
y  ㄗ
z  ㄈ
%keyname end
%chardef begin
3 ˇ
4 ˋ
6 ˊ
7 ˙
-3 洱
-3 餌
-3 邇
%chardef end
```

CIN 表格中大部份的內容為 key/value 組合，以空白或 Tab 區分。

非必要或常省略項目:

* \#: # 符號及其後所有的內容為注解
* %gen_inp: General Input 輸入模組，由於幾乎無其他輸入模組，因此多半省略
* %encoding: 編碼格式，如 UTF-8 
* %endkey: 組字結束鍵，相當於按下空白鍵，例如注音輸入法的聲調鍵 3467

必要項目:

* %?name: 輸入法名稱，依不同的語系常見的有 name, ename, cname 等名稱，至少一項
* %selkey: 候選字選字鍵
* %keyname begin/end: 輸入法使用按鍵定義區段。分別為按鍵(無大小寫區分)及其按鍵代表的結果，通常為輸入法字根。  
例如注音輸入法 "1" 為 "ㄅ"，"q" 為 "ㄆ"
* %chardef begin/end: 字根組合及結果區段。每一個組合及結果為一行，同一個字根組合可以有數種結果，字根無大小寫區分。  
例如注音輸入法 "-3" (ㄦˇ) 結果有 "洱"、"餌"、"邇"等多種結果

## 輸入法字根蒐集列表

此為公眾授權或已無法追本溯源的 CIN 表格蒐集，底下列表為參考清單，實際請直接瀏灠此目錄。
Frankie 及 OkidoKey 並未使用內建目錄中所有表格。s

#### 繁體中文表格

```
array10 - 行列 10 a/b/c
array26 - 行列廿六
array30_OkidoKey - 行列 30
array30 - 行列 30
array40 - 行列 40
biaoyin - 表音
bpmf-cns - 全字庫注音(精簡版)
bpmf-ext - 注音
bpmf-Hsu - 注音-許氏鍵盤
bpmf - 注音
cangjie6 - 倉頡六代
cj-ext - 倉頡（大字集）
cj-j - 倉頡-J
cj-wildcard - 倉頡（萬用字元版）
cj - 倉頡
cj5 - 倉頡五代
corner - 四角號碼
daibuun - 普實台文
dayi3-patched - 大易 (標點符號版)
dayi3 - 大易
dayi4 - 大易四碼
freenewcj - 自由大新
jinjin - 晶晶碼
jyut6ping3-toneless - 粵語拼音 (無調號版)
jyut6ping3 - 粵語拼音
NewCJ3 - 亂倉打鳥
ov_ez - 輕鬆
ov_ez75 - 輕鬆 2006 原味版 (for 香草)
ov_ezbig - 輕鬆大詞庫
ov_ezsmall - 輕鬆小詞庫
pictograph - 華象直覺
pinyinbig5 - 正體漢語拼音
poj-holo - 白話字漢羅
qcj - 順序速成
scj6 - 快倉六
scj7 - 快倉七代
simplex-ext - 簡易（大字集）
simplex - 簡易（速成）
stroke-bsm - 王頌平教授筆順碼輸入法
stroke-g6code - 布禮文博士六碼筆畫輸入法
stroke-stroke5 - 香港長者資訊天地筆順五碼
stroke-stroke5-keypad - 香港長者資訊天地筆順五碼 (數字鍵版)
taiwain-minnan-zhuyin - 台式閩南語注音
tcj - 繁倉
tp_hakka_hl - 通用拼音客家話 海陸腔
tp_hakka_sy - 通用拼音客家話 四縣腔
wu - 吳語注音法（完整）
```

#### 簡體中文表格

```
ghcm - 矧码
jidianwubi - 极点五笔
jtcj - 简体仓颉
lxsy_0.40 - 灵形速影
lxsy_0.41 - 灵形速影 (词)
pinyin - 简体汉語拼音
shuangpin - 简体双拼
wubizixing - 简体五笔字形
zhengma - 中易郑码
```
