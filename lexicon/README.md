# Lexicon

字詞庫 CSV 檔案不含欄位名稱，分為字詞、比重及拼音(不含空白)三欄，以 Tab 區分  

    一丁不識	0	yidingbushi
    一丘之貉	0	yiqiuzhihao
    一了百了	0	yilebaile

除了因格式轉換所需的內容變更，另外也排除僅有一個字的字詞  
來源無拼音資料時，則另產生無調號漢語拼音(CFStringTransform)  

####教育部相關詞典
刪除部份異體字/缺字的字詞。  
重編國語辭典則參考酷音詞庫，取其相同字詞的比重。  

####结巴中文分词
保留字詞比重，刪除詞性標記。

####開放粵語詞典
以粵併繁體詞典，刪除國語解釋。
合併粵典的語料庫x詞表使用頻率做比重。

####粵典
以粵典詞表，取第一個拼音方式，搭配語料庫x詞表使用頻率做為比重。

## Resources

MoE-Revised.csv - 教育部《重編國語辭典 修訂本》，版本編號：2015_20180409  
MoE-concised.csv - 教育部《國語辭典簡編本》，版本編號：2014_20180611  
MoE-idioms.csv - 教育部《成語典》，版本編號：2011_20180517  
McBopomofo-phrase.csv - 小麥注音輸入法 phrase.occ  
Jieba-hans.csv - 结巴中文分词 dict.txt  
kfcd-yp.csv - 開放粵語詞典（粵拼版）cidian_zhyue-ft-kfcd-yp-2019623.txt  
wordshk.csv - 粵典詞表 2020/05/15 wordslist.json, existingwordcount.json

## License

教育部國語辭典公眾授權網 - CCPL  
https://resources.publicense.moe.edu.tw  

OpenVanilla McBopomofo 小麥注音輸入法 - MIT  
https://github.com/openvanilla/McBopomofo/tree/master/Source/Data  

结巴中文分词 - MIT  
https://github.com/fxsjy/jieba  

開放粵語詞典 - CC 3.0  
http://www.kaifangcidian.com  

粵典詞表 - Public Domain  
https://words.hk  