# Lexicon

以原公眾授權詞庫，僅取二字(含)以上的字詞，並加上無調號漢語拼音(CFStringTransform)  

教育部相關詞典，刪除部份異體字/缺字的字詞。重編國語辭典則參考酷音詞庫，取其相同字詞的比重。  
结巴中文分词，保留字詞比重，刪除詞性標記
開放粵語詞典，以粵併繁體詞典，刪除國語解釋

CSV 檔案不含欄位名稱，分為字詞、比重及拼音三欄，以 Tab 區分  
目前整理過後的字詞以比重大至小排序  

### Resources

MoE-Revised.csv - 教育部《重編國語辭典 修訂本》，版本編號：2015_20180409  
MoE-concised.csv - 教育部《國語辭典簡編本》，版本編號：2014_20180611  
MoE-idioms.csv - 教育部《成語典》，版本編號：2011_20180517  
McBopomofo-phrase.csv - 小麥注音輸入法 phrase.occ  
Jieba-hans.csv - 结巴中文分词 dict.txt  
kfcd-yp.csv - 開放粵語詞典（粵拼版）cidian_zhyue-ft-kfcd-yp-2019623.txt  

### License

教育部國語辭典公眾授權網 - CCPL  
https://resources.publicense.moe.edu.tw  

OpenVanilla McBopomofo 小麥注音輸入法 - MIT  
https://github.com/openvanilla/McBopomofo/tree/master/Source/Data  

结巴中文分词 - MIT  
https://github.com/fxsjy/jieba  

開放粵語詞典（粵拼版）- CC 3.0  
http://www.kaifangcidian.com  
