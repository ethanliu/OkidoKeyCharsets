# Lexicon

字詞 CSV 檔案不含欄位名稱，分為字詞、比重及拼音(不含空白)三欄，應以 Tab 區分。  

    氓	0	mang
    氓	0	meng
    盲從	0	mangcong
    盲人摸象	0	mangrenmoxiang
    盲人	0	mangren
    盲腸	0	mangchang
    盲腸炎	0	mangchangyan
    盲點	0	mangdian
    盲目	0	mangmu
    盲胞	0	mangbao
    芒刺在背	0	mangcizaibei
    一丁不識	0	yidingbushi
    一丘之貉	0	yiqiuzhihao
    一了百了	0	yilebaile

比重為數值，數值越大優先權越高。    
拼音並不限於漢語拼音，但仍應為連續不含空白及調號的英文為主。  
若來源無資訊可供轉換拼音時，則另以 CFStringTransform 產生無調號漢語拼音，但此方式無法兼顧多音字詞，所以並不能保證全部正確。  
若無另行標識時，其內容為繁體中文字詞  

所有字詞各別的說明及其授權方式，請參閱同檔名的 .txt 文件。  
