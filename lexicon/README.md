# Lexicon

字詞庫 CSV 檔案不含欄位名稱，分為字詞、比重及拼音(不含空白)三欄，以 Tab 區分  

    一丁不識	0	yidingbushi
    一丘之貉	0	yiqiuzhihao
    一了百了	0	yilebaile

除了因格式轉換所需的內容變更，另外也排除僅有一個字的字詞  
來源無拼音資料時，則另產生無調號漢語拼音 (CFStringTransform)  
無另外標識時，為繁體中文字詞  

#### 教育部相關詞典
刪除部份異體字/缺字的字詞。  
重編國語辭典則參考酷音詞庫，取其相同字詞的比重。  

#### 结巴中文分词 (簡體)
保留字詞比重，刪除詞性標記。

#### Rime 粵語拼音方案
取自 Rime 粵語拼音方案 jyut6ping3.dict.yaml 中的詞彙內容。  

## Resources

MoE-Revised.csv - 教育部《重編國語辭典 修訂本》，版本編號：2015_20180409  
MoE-concised.csv - 教育部《國語辭典簡編本》，版本編號：2014_20180611  
MoE-idioms.csv - 教育部《成語典》，版本編號：2011_20180517  
McBopomofo-phrase.csv - 小麥注音輸入法 phrase.occ  
Jieba-hans.csv - 结巴中文分词 dict.txt  
Rime-cantonese.csv - Rime 粵語拼音方案，版本: 2020.05.19  

## License

教育部國語辭典公眾授權網 - CCPL  
https://resources.publicense.moe.edu.tw  

OpenVanilla McBopomofo 小麥注音輸入法 - MIT  
https://github.com/openvanilla/McBopomofo/tree/master/Source/Data  

结巴中文分词 - MIT  
https://github.com/fxsjy/jieba  

Rime 粵語拼音方案 - CC 4.0  
https://github.com/rime/rime-cantonese  

