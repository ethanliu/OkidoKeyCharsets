## CIN 輸入法表格

cin 表格為 gcin, xcin, scim 等輸入法引擎使用的資料格式。  
cin 表格包含輸入法名稱，使用按鍵及字根組合等輸入法相關內容的純文字文件。  
以注音輸入法為例，其內容如下:

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

cin 表格中大部份的內容為 key/value 組合，以空白或 Tab 區分。

非必要或常省略項目:

* #: # 符號及其後所有的內容為注解
* %gen_inp: General Input 輸入模組，由於幾乎無其他輸入模組，因此多半省略
* %encoding: 編碼格式，如 UTF-8 
* %endkey: 組字結束鍵，相當於按下空白鍵，例如注音輸入法的聲調鍵 3467

必要項目:

* %?name: 輸入法名稱，依不同的語系常見的有 ename, cname, sname, tcname, tsname 等名稱
* %selkey: 候選字選字鍵
* %keyname begin/end: 輸入法使用按鍵定義區段。分別為按鍵(無大小寫區分)及其按鍵代表的結果，通常為輸入法字根。  
例如注音輸入法 "1" 為 "ㄅ"，"q" 為 "ㄆ"
* %chardef begin/end: 字根組合及結果區段。每一個組合及結果為一行，同一個字根組合可以有數種結果，字根無大小寫區分。  
例如注音輸入法 "-3" (ㄦˇ) 結果有 "洱"、"餌"、"邇"等多種結果

## 輸入法字根蒐集列表

此為公眾授權或已無法追本溯源的 cin 表格蒐集


    array10a.cin - 行列 10
    array26.cin - 行列廿六
    array30_OkidoKey_0.75.cin - 行列 30
    array30.cin - 行列 30
    array40.cin - 行列 40
    biaoyin.cin - 表音
    bpmf-cns.cin - 全字庫注音(精簡版)
    bpmf-ext.cin - 注音
    bpmf-Hsu.cin - 注音-許氏鍵盤
    bpmf.cin - 注音
    cangjie6.cin - 倉頡六代
    cj-ext.cin - 倉頡（大字集）
    cj-j.cin - 倉頡-J
    cj-wildcard.cin - 倉頡（萬用字元版）
    cj.cin - 倉頡
    cj5.cin - 倉頡五代
    CnsPhonetic2016-08_GCINv2 - 全字庫注音2016-08
    corner.cin - 四角號碼
    daibuun.cin - 普實台文
    dayi3-patched.cin - 大易 (標點符號版)
    dayi3.cin - 大易
    ehq-symbols.cin - 漁村符號及日文假名
    freenewcj.cin - 自由大新
    jidianwubi.cin - 极点五笔
    jinjin.cin - 晶晶碼
    jtcj.cin - 简体仓颉
    jyutping-toneless.cin - 粵語拼音 (無調號版)
    jyutping.cin - 粵語拼音
    lxsy_0.40.cin - 灵形速影
    lxsy_0.41.cin - 灵形速影 (词)
    NewCJ3.cin - 亂倉打鳥
    ov_ez.cin - 輕鬆
    ov_ez75.cin - 輕鬆 2006 原味版 (for 香草)
    ov_ezbig.cin - 輕鬆大詞庫
    ov_ezsmall.cin - 輕鬆小詞庫
    pictograph.cin - 華象直覺
    pinyin.cin - 简体汉語拼音
    pinyinbig5.cin - 正體漢語拼音
    poj-holo.cin - 白話字漢羅
    qcj.cin - 順序速成
    scj6.cin - 快倉六
    scj7.cin - 快倉七代
    shuangpin.cin - 简体双拼
    simplex-ext.cin - 簡易（大字集）
    simplex.cin - 簡易（速成）
    taiwain-minnan-zhuyin.cin - 台式閩南語注音
    tcj.cin - 繁倉
    tp_hakka_hl.cin - 通用拼音客家話 海陸腔
    tp_hakka_sy.cin - 通用拼音客家話 四縣腔
    wu.cin - 吳語注音法（完整）
    wubizixing.cin - 简体五笔字形
    wus.cin - 吴语注音法（简體）
    wut.cin - 吳語注音法（正體）

