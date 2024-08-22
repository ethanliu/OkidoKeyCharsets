.PHONY: usage clear

# the syntax of sed in this Makefile is specified for macOS

TABLE_DIR := table
LEXICON_DIR := lexicon

define SYNOPSIS
@echo "Upstream :: update upstream and local repositories"
@echo "update - update all exclude moe"
@echo "moe - update moe"
endef

usage:
	@echo ${SYNOPSIS}

update: pull patch
	@echo "Update local files..."
	@cp rawdata/cin-tables/bsm.cin ${TABLE_DIR}/stroke-bsm.cin
	@cp rawdata/cin-tables/g6code.cin ${TABLE_DIR}/stroke-g6code.cin
	@echo "fin."

pull:
	@echo "Upstream pulling..."
	@for path in array10 array30 ghcm jieba rime-cantonese McBopomofo cin-tables; do \
		echo "🤝 $${path}"; \
		cd "rawdata/$${path}" && git pull && cd ../..; \
	done;

patch: array10 array30 ghcm jyutping mcbpmf

# moe requires manually download files process
moe: moe-idioms moe-concised moe-revised

# uptreams

array10:
	@echo "Patching array10..."
	@$(eval file := $(wildcard rawdata/array10/OpenVanilla/array10a*.cin))
	@cp ${file} ${TABLE_DIR}/array10a.cin
	@$(eval file := $(wildcard rawdata/array10/OpenVanilla/array10b*.cin))
	@cp ${file} ${TABLE_DIR}/array10b.cin
	@$(eval file := $(wildcard rawdata/array10/OpenVanilla/array10c*.cin))
	@cp ${file} ${TABLE_DIR}/array10c.cin

array30:
	@echo "Patching array30..."
	@$(eval file := $(wildcard rawdata/array30/OpenVanilla/array30*.cin))
	@cp ${file} ${TABLE_DIR}/array30.cin
	@$(eval file := $(wildcard rawdata/array30/OpenVanilla/array-special*.cin))
	@cp ${file} ${TABLE_DIR}/array-special.cin
	@$(eval file := $(wildcard rawdata/array30/OpenVanilla/array-shortcode*.cin))
	@cp ${file} ${TABLE_DIR}/array-shortcode.cin
	@$(eval file := $(wildcard rawdata/array30/OkidoKey/array30-OkidoKey-regular*.cin))
	@cp ${file} ${TABLE_DIR}/array30-OkidoKey.cin
	@$(eval file := $(wildcard rawdata/array30/OkidoKey/array30-OkidoKey-big*.cin))
	@cp ${file} ${TABLE_DIR}/array30-OkidoKey-big.cin

	@cat ${TABLE_DIR}/array-special.cin | sed -n '/%chardef begin/,/%chardef end/p' | sed 's/chardef/special/g' > tmp/array-special.cin
	@cat ${TABLE_DIR}/array-shortcode.cin | sed -n '/%chardef begin/,/%chardef end/p' | sed 's/chardef/shortcode/g' > tmp/array-shortcode.cin
	@cat tmp/array-shortcode.cin >> ${TABLE_DIR}/array30-OkidoKey.cin
	@cat tmp/array-special.cin >> ${TABLE_DIR}/array30-OkidoKey.cin
	@cat tmp/array-shortcode.cin >> ${TABLE_DIR}/array30-OkidoKey-big.cin
	@cat tmp/array-special.cin >> ${TABLE_DIR}/array30-OkidoKey-big.cin
	@-rm tmp/array-special.cin tmp/array-shortcode.cin

	@echo "Patching array phrase..."
	@$(eval file := $(wildcard rawdata/array30/array30-phrase*.txt))
	@bin/txt2csv.py -i ${file} -o ${LEXICON_DIR}/array30.csv -c 3 1 0

# @#$(eval txt := '\#\ shortcode\ +\ special\\n')
# @##sed -i '' -e 's/%gen_inp/${txt}\n%gen_inp/g' ${TABLE_DIR}/array30.cin
# @#sed -i '' -e 's/%gen_inp/${txt}\n%gen_inp/g' ${TABLE_DIR}/array30-OkidoKey.cin
# @#sed -i '' -e 's/%gen_inp/${txt}\n%gen_inp/g' ${TABLE_DIR}/array30-OkidoKey-big.cin

ghcm:
	@echo "Patching ghcm..."
	@bin/rime2cin.py -i rawdata/ghcm/SM.dict.yaml -o ${TABLE_DIR}/ghcm.cin -x rawdata/misc/ghcm-header.cin

jyutping:
	@echo "Patching jyutping..."
	@bin/jyutping-rime.py -i rawdata/rime-cantonese/jyut6ping3.chars.dict.yaml -o ${TABLE_DIR}/jyut6ping3.cin -t tone --header rawdata/misc/jyut6ping3-header.cin
	@bin/jyutping-rime.py -i rawdata/rime-cantonese/jyut6ping3.chars.dict.yaml -o ${TABLE_DIR}/jyut6ping3-toneless.cin -t toneless --header rawdata/misc/jyut6ping3-toneless-header.cin
	@echo "Patching jyutping phrase..."
	@bin/jyutping-rime.py -i rawdata/rime-cantonese/jyut6ping3.words.dict.yaml -o ${LEXICON_DIR}/jyutping.csv -t phrase

moe-revised:
	@$(eval version = $(notdir $(wildcard rawdata/moe/src/dict_revised_*.xlsx)))
	@$(eval version = $(shell echo '${version}' | sed 's/dict_revised_\(.*\)\.xlsx/\1/' ))
	@echo "revised: ${version}"
	@in2csv rawdata/moe/src/dict_revised_${version}.xlsx > rawdata/moe/revised-raw.csv
	@csvcut -c 字詞號,字詞名,注音一式,漢語拼音,多音參見訊息 rawdata/moe/revised-raw.csv > rawdata/moe/revised.csv
	@-rm rawdata/moe/revised-raw.csv
	@sed -i '' -e 's/編號 .* 版本/編號 ${version} 版本/g' ${LEXICON_DIR}/moe-revised.csv.txt
	@bin/moe2csv.py -i rawdata/moe/revised.csv -o ${LEXICON_DIR}/moe-revised.csv

# original dict_idioms_2020_20230629.xls cam with incomplete fomular binding to foreign file
# must manually save as another copy to fix above question before using csvkit
moe-idioms:
	@$(eval version = $(notdir $(wildcard rawdata/moe/src/dict_idioms_*.xls)))
	@$(eval version = $(shell echo '${version}' | sed 's/dict_idioms_\(.*\)\.xls/\1/' ))
	@echo "idioms: ${version}"
	@in2csv rawdata/moe/src/dict_idioms_${version}.xls > rawdata/moe/idioms-raw.csv
	@csvcut -c 編號,成語,注音,漢語拼音 rawdata/moe/idioms-raw.csv > rawdata/moe/idioms.csv
	@-rm rawdata/moe/idioms-raw.csv
	@sed -i '' -e 's/編號 .* 版本/編號 ${version} 版本/g' ${LEXICON_DIR}/moe-idioms.csv.txt
	@bin/moe2csv.py -i rawdata/moe/idioms.csv -o ${LEXICON_DIR}/moe-idioms.csv

moe-concised:
	@$(eval version = $(notdir $(wildcard rawdata/moe/src/dict_concised_*.xlsx)))
	@$(eval version = $(shell echo '${version}' | sed 's/dict_concised_\(.*\)\.xlsx/\1/' ))
	@echo "concised: ${version}"
	@in2csv rawdata/moe/src/dict_concised_${version}.xlsx > rawdata/moe/concised-raw.csv
	@csvcut -c 字詞號,字詞名,注音一式,漢語拼音,多音參見訊息 rawdata/moe/concised-raw.csv > rawdata/moe/concised.csv
	@-rm rawdata/moe/concised-raw.csv
	@sed -i '' -e 's/編號 .* 版本/編號 ${version} 版本/g' ${LEXICON_DIR}/moe-concised.csv.txt
	@bin/moe2csv.py -i rawdata/moe/concised.csv -o ${LEXICON_DIR}/moe-concised.csv

mcbpmf:
	@bin/mcbpmf2csv.py -i rawdata/McBopomofo/Source/Data/phrase.occ -o ${LEXICON_DIR}/mcbopomofo.csv

