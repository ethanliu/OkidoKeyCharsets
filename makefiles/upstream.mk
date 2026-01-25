.PHONY: usage clear build
include config.mk

# the syntax of sed in this Makefile is specified for macOS

define SYNOPSIS

@echo "Upstream :: update upstream and local repositories"
@echo "update - update all"

endef

usage:
	@echo $(SYNOPSIS)

pull:
	@echo "Upstream pulling..."
	@for path in array10 array30 ghcm jieba rime-cantonese McBopomofo cin-tables; do \
		echo "🤝 $${path}"; \
		cd "$(RAWDATA_DIR)/$${path}" && git pull --rebase --autostash && cd ../..; \
	done;

update: pull patch
	@echo "Update local files..."
	@cp $(RAWDATA_DIR)/cin-tables/bsm.cin $(TABLE_DIR)/stroke-bsm.cin
	@cp $(RAWDATA_DIR)/cin-tables/g6code.cin $(TABLE_DIR)/stroke-g6code.cin
	@echo "fin."

patch: array10 ghcm jyutping mcbpmf

# uptreams

array10:
	@echo "Patching array10..."
	@$(eval file := $(wildcard $(RAWDATA_DIR)/array10/OpenVanilla/array10a*.cin))
	@cp ${file} $(TABLE_DIR)/array10a.cin
	@$(eval file := $(wildcard $(RAWDATA_DIR)/array10/OpenVanilla/array10b*.cin))
	@cp ${file} $(TABLE_DIR)/array10b.cin
	@$(eval file := $(wildcard $(RAWDATA_DIR)/array10/OpenVanilla/array10c*.cin))
	@cp ${file} $(TABLE_DIR)/array10c.cin

array30:
	@echo "Patching array30..."
	@$(eval file := $(wildcard $(RAWDATA_DIR)/array30/OpenVanilla/array30*.cin))
	@cp ${file} $(TABLE_DIR)/array30.cin
	@$(eval file := $(wildcard $(RAWDATA_DIR)/array30/OpenVanilla/array-special*.cin))
	@cp ${file} $(TABLE_DIR)/array-special.cin
	@$(eval file := $(wildcard $(RAWDATA_DIR)/array30/OpenVanilla/array-shortcode*.cin))
	@cp ${file} $(TABLE_DIR)/array-shortcode.cin
	@$(eval file := $(wildcard $(RAWDATA_DIR)/array30/OkidoKey/array30-OkidoKey-regular*.cin))
	@cp ${file} $(TABLE_DIR)/array30-OkidoKey.cin
	@$(eval file := $(wildcard $(RAWDATA_DIR)/array30/OkidoKey/array30-OkidoKey-big*.cin))
	@cp ${file} $(TABLE_DIR)/array30-OkidoKey-big.cin

# 	@TEXT="#\n# 此表格包含簡碼 (%%shortcode) 及特別碼 (%%special)\n#" ; \
# 	printf "$$TEXT\n" | sed -i '' '5r /dev/stdin' $(TABLE_DIR)/array30-OkidoKey.cin

# 	@TEXT="#\n# 此表格包含簡碼 (%%shortcode) 及特別碼 (%%special)\n#" ; \
# 	printf "$$TEXT\n" | sed -i '' '5r /dev/stdin' $(TABLE_DIR)/array30-OkidoKey-big.cin

# 	@cat $(TABLE_DIR)/array-special.cin | sed -n '/%chardef begin/,/%chardef end/p' | sed 's/chardef/special/g' > tmp/array-special.cin
# 	@cat $(TABLE_DIR)/array-shortcode.cin | sed -n '/%chardef begin/,/%chardef end/p' | sed 's/chardef/shortcode/g' > tmp/array-shortcode.cin
# 	@cat tmp/array-shortcode.cin >> $(TABLE_DIR)/array30-OkidoKey.cin
# 	@cat tmp/array-special.cin >> $(TABLE_DIR)/array30-OkidoKey.cin
# 	@cat tmp/array-shortcode.cin >> $(TABLE_DIR)/array30-OkidoKey-big.cin
# 	@cat tmp/array-special.cin >> $(TABLE_DIR)/array30-OkidoKey-big.cin
# 	@-rm tmp/array-special.cin tmp/array-shortcode.cin

# 	@echo "Patching array phrase..."
# 	@$(eval file := $(wildcard $(RAWDATA_DIR)/array30/array30-phrase*.txt))
# 	@$(BIN_DIR)/txt2csv.py -i ${file} -o $(LEXICON_DIR)/array30.csv -c 3 1 0

# @#$(eval txt := '\#\ shortcode\ +\ special\\n')
# @##sed -i '' -e 's/%gen_inp/${txt}\n%gen_inp/g' $(TABLE_DIR)/array30.cin
# @#sed -i '' -e 's/%gen_inp/${txt}\n%gen_inp/g' $(TABLE_DIR)/array30-OkidoKey.cin
# @#sed -i '' -e 's/%gen_inp/${txt}\n%gen_inp/g' $(TABLE_DIR)/array30-OkidoKey-big.cin

# array30:
# 	@echo "Patching array30..."
# 	@$(eval file := $(wildcard $(RAWDATA_DIR)/array30/OpenVanilla/array30*.cin))
# 	@cp ${file} $(TABLE_DIR)/array30.cin
# 	@$(eval file := $(wildcard $(RAWDATA_DIR)/array30/OpenVanilla/array-special*.cin))
# 	@cp ${file} $(TABLE_DIR)/array-special.cin
# 	@$(eval file := $(wildcard $(RAWDATA_DIR)/array30/OpenVanilla/array-shortcode*.cin))
# 	@cp ${file} $(TABLE_DIR)/array-shortcode.cin
# 	@$(eval file := $(wildcard $(RAWDATA_DIR)/array30/OkidoKey/array30-OkidoKey-regular*.cin))
# 	@cp ${file} $(TABLE_DIR)/array30-OkidoKey.cin
# 	@$(eval file := $(wildcard $(RAWDATA_DIR)/array30/OkidoKey/array30-OkidoKey-big*.cin))
# 	@cp ${file} $(TABLE_DIR)/array30-OkidoKey-big.cin

# 	@$(eval phrasefile := $(wildcard $(RAWDATA_DIR)/array30/array30-phrase*.txt))
# 	@$(BIN_DIR)/txt2csv.py -i ${phrasefile} -o $(LEXICON_DIR)/array30.csv -c 3 1 0

# 	@TEXT="#\n# 此表格包含簡碼 (%%shortcode) 及特別碼 (%%special)\n#" ; \
# 	printf "$$TEXT\n" | sed -i '' '5r /dev/stdin' $(TABLE_DIR)/array30-OkidoKey.cin ; \
# 	printf "$$TEXT\n" | sed -i '' '5r /dev/stdin' $(TABLE_DIR)/array30-OkidoKey-big.cin ;

# 	@cp $(TABLE_DIR)/array30-OkidoKey.cin $(TABLE_DIR)/array30-OkidoKey-phrase.cin
# 	@cp $(TABLE_DIR)/array30-OkidoKey-big.cin $(TABLE_DIR)/array30-OkidoKey-big-phrase.cin

# 	@TEXT="# 及行列輸入法官方收錄 6 萬詞的詞庫檔\n#" ; \
# 	printf "$$TEXT\n" | sed -i '' '7r /dev/stdin' $(TABLE_DIR)/array30-OkidoKey-phrase.cin ; \
# 	printf "$$TEXT\n" | sed -i '' '7r /dev/stdin' $(TABLE_DIR)/array30-OkidoKey-big-phrase.cin ;

# 	@sed -i '' 's/^%chardef end/ /' $(TABLE_DIR)/array30-OkidoKey-phrase.cin
# 	@cat ${phrasefile} >> $(TABLE_DIR)/array30-OkidoKey-phrase.cin
# 	@echo "%chardef end\n" >> $(TABLE_DIR)/array30-OkidoKey-phrase.cin

# 	@sed -i '' 's/^%chardef end/ /' $(TABLE_DIR)/array30-OkidoKey-big-phrase.cin
# 	@cat ${phrasefile} >> $(TABLE_DIR)/array30-OkidoKey-big-phrase.cin
# 	@echo "%chardef end\n" >> $(TABLE_DIR)/array30-OkidoKey-big-phrase.cin

# 	@cat $(TABLE_DIR)/array-special.cin | sed -n '/%chardef begin/,/%chardef end/p' | sed 's/chardef/special/g' > tmp/array-special.cin
# 	@cat $(TABLE_DIR)/array-shortcode.cin | sed -n '/%chardef begin/,/%chardef end/p' | sed 's/chardef/shortcode/g' > tmp/array-shortcode.cin

# 	@for path in $(TABLE_DIR)/array30-OkidoKey*.cin ; do \
# 		cat tmp/array-shortcode.cin >> $${path} ; \
# 		cat tmp/array-special.cin >> $${path} ; \
# 	done


ghcm:
	@echo "Patching ghcm..."
	@$(BIN_DIR)/rime2cin.py -i $(RAWDATA_DIR)/ghcm/SM.dict.yaml -o $(TABLE_DIR)/ghcm.cin -x $(MISC_DIR)/ghcm-header.cin

jieba:
	@echo "Patching jieba..."
	@$(BIN_DIR)/jieba2csv.py -i $(RAWDATA_DIR)/jieba/jieba/dict.txt -o ${LEXICON_DIR}/jieba.csv


jyutping:
	@echo "Patching jyutping..."
	@$(BIN_DIR)/jyutping-rime.py -i $(RAWDATA_DIR)/rime-cantonese/jyut6ping3.chars.dict.yaml -o $(TABLE_DIR)/jyut6ping3.cin -t tone --header $(MISC_DIR)/jyut6ping3-header.cin
	@$(BIN_DIR)/jyutping-rime.py -i $(RAWDATA_DIR)/rime-cantonese/jyut6ping3.chars.dict.yaml -o $(TABLE_DIR)/jyut6ping3-toneless.cin -t toneless --header $(MISC_DIR)/jyut6ping3-toneless-header.cin
	@echo "Patching jyutping phrase..."
	@$(BIN_DIR)/jyutping-rime.py -i $(RAWDATA_DIR)/rime-cantonese/jyut6ping3.words.dict.yaml -o $(LEXICON_DIR)/jyutping.csv -t phrase --header $(LEXICON_DIR)/jyutping.csv.txt

mcbpmf:
# @$(BIN_DIR)/mcbpmf2csv.py -i $(RAWDATA_DIR)/McBopomofo/Source/Data/phrase.occ -o $(LEXICON_DIR)/mcbopomofo.csv
	@$(BIN_DIR)/mcbpmf2csv.py -i $(RAWDATA_DIR)/McBopomofo/Source -o $(LEXICON_DIR)/mcbopomofo.csv

# moe:
# 	@curl -o $(RAWDATA_DIR)/moe/sutian.json https://raw.githubusercontent.com/g0v/moedict-webkit/refs/heads/master/t/index.json
# 	@curl -o $(RAWDATA_DIR)/moe/hakka.json https://raw.githubusercontent.com/g0v/moedict-webkit/refs/heads/master/h/index.json