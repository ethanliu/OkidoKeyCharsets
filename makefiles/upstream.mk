.PHONY: usage clear
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

patch: array10 array30 ghcm jyutping mcbpmf

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

	@cat $(TABLE_DIR)/array-special.cin | sed -n '/%chardef begin/,/%chardef end/p' | sed 's/chardef/special/g' > tmp/array-special.cin
	@cat $(TABLE_DIR)/array-shortcode.cin | sed -n '/%chardef begin/,/%chardef end/p' | sed 's/chardef/shortcode/g' > tmp/array-shortcode.cin
	@cat tmp/array-shortcode.cin >> $(TABLE_DIR)/array30-OkidoKey.cin
	@cat tmp/array-special.cin >> $(TABLE_DIR)/array30-OkidoKey.cin
	@cat tmp/array-shortcode.cin >> $(TABLE_DIR)/array30-OkidoKey-big.cin
	@cat tmp/array-special.cin >> $(TABLE_DIR)/array30-OkidoKey-big.cin
	@-rm tmp/array-special.cin tmp/array-shortcode.cin

	@echo "Patching array phrase..."
	@$(eval file := $(wildcard $(RAWDATA_DIR)/array30/array30-phrase*.txt))
	@$(BIN_DIR)/run.sh txt2csv.py -i ${file} -o $(LEXICON_DIR)/array30.csv -c 3 1 0

# @#$(eval txt := '\#\ shortcode\ +\ special\\n')
# @##sed -i '' -e 's/%gen_inp/${txt}\n%gen_inp/g' $(TABLE_DIR)/array30.cin
# @#sed -i '' -e 's/%gen_inp/${txt}\n%gen_inp/g' $(TABLE_DIR)/array30-OkidoKey.cin
# @#sed -i '' -e 's/%gen_inp/${txt}\n%gen_inp/g' $(TABLE_DIR)/array30-OkidoKey-big.cin

ghcm:
	@echo "Patching ghcm..."
	@$(BIN_DIR)/run.sh rime2cin.py -i $(RAWDATA_DIR)/ghcm/SM.dict.yaml -o $(TABLE_DIR)/ghcm.cin -x $(RAWDATA_DIR)/misc/ghcm-header.cin

jyutping:
	@echo "Patching jyutping..."
	@$(BIN_DIR)/run.sh jyutping-rime.py -i $(RAWDATA_DIR)/rime-cantonese/jyut6ping3.chars.dict.yaml -o $(TABLE_DIR)/jyut6ping3.cin -t tone --header $(RAWDATA_DIR)/misc/jyut6ping3-header.cin
	@$(BIN_DIR)/run.sh jyutping-rime.py -i $(RAWDATA_DIR)/rime-cantonese/jyut6ping3.chars.dict.yaml -o $(TABLE_DIR)/jyut6ping3-toneless.cin -t toneless --header $(RAWDATA_DIR)/misc/jyut6ping3-toneless-header.cin
	@echo "Patching jyutping phrase..."
	@$(BIN_DIR)/run.sh jyutping-rime.py -i $(RAWDATA_DIR)/rime-cantonese/jyut6ping3.words.dict.yaml -o $(LEXICON_DIR)/jyutping.csv -t phrase --header $(LEXICON_DIR)/jyutping.csv.txt

mcbpmf:
	@echo "NOTE: moe must be ready before running this task"
	@$(BIN_DIR)/run.sh mcbpmf2csv.py -i $(RAWDATA_DIR)/McBopomofo/Source/Data/phrase.occ -o $(LEXICON_DIR)/mcbopomofo.csv

