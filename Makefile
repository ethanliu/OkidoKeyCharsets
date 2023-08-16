.PHONY: usage all clear test table lexicon dist

TABLE_DIR := table
LEXICON_DIR := lexicon
DIST_DIR := dist

QUEUE_DIR := queue
GITEE_DIR := gitee
GITHUB_DIR := github

TABLE_DIST_PATH := ${DIST_DIR}/${QUEUE_DIR}/${TABLE_DIR}
LEXICON_DIST_PATH := ${DIST_DIR}/${QUEUE_DIR}/${LEXICON_DIR}
SRC_PATH := ../src/baker/baker/Supporting\ Files/

define SYNOPSIS

@echo "OkidoKey/Frankie Makefile"
@echo ""
@echo "Resources:"
@echo "    init - Initial dist folder"
@echo "    table - Generate db splits and DataTables.json"
@echo "    lexicon - Generate db splits Lexicon.json"
@echo "    keyboard - Generate KeyboardLayouts.json"
@echo "    dist - Copy resources to Xcode codebase and Gitee repo"
@echo "    splits - "
@echo "    clear - Clear dist"
@echo ""
@echo "    table-db - Build all CIN table databases"
@echo "    lexicon-db - Build all lexicon databases"
@echo "    emoji-db - Build emoji.db"
@echo "    char-db - Build Character.db"
@echo "    unihan-db - Build Unihan.db"
@echo ""
@echo "3rd party repositories:"
@echo "    pull - Update all upstream repos"
@echo "    array10 - Array10 [a/b/c] table builder"
@echo "    array30 - Array30 [ov/OkidoKey] table builder"
@echo "    array-phrase - Array30-phrase lexicon builder"
@echo "    bossy - Custom boshiamy table builder"
@echo "    ghcm - ghcm table builder"
@echo "    jieba - Jieba lexicon builder"
@echo "    jyutping - Jyutping from rime-cantonese table builder"
@echo "    jyutping-phrase - Rime-cantonese lexicon builder"
@echo "    mcbpmf - McBopomofo lexicon builder"
@echo "    moe-csv - Convert CSV from original MoE XLS files"
@echo "    moe-db - MoE concised, idioms, revised lexicon builder"
@echo ""

endef

# alternative to time command

define timeStart
	@date +%s > tmp.timestamp
endef

define timeStop
	@echo "\n...took $$(($$(date +%s)-$$(cat tmp.timestamp))) seconds.\n"
	@-rm tmp.timestamp
endef

usage:
	@echo ${SYNOPSIS}

test:
	@echo test

init:
	@mkdir -p ${DIST_DIR}/${QUEUE_DIR}/${TABLE_DIR}
	@mkdir -p ${DIST_DIR}/${QUEUE_DIR}/${LEXICON_DIR}
	@mkdir -p ${DIST_DIR}/${GITHUB_DIR}/${TABLE_DIR}
	@mkdir -p ${DIST_DIR}/${GITHUB_DIR}/${LEXICON_DIR}
	@mkdir -p ${DIST_DIR}/${GITEE_DIR}/${TABLE_DIR}
	@mkdir -p ${DIST_DIR}/${GITEE_DIR}/${LEXICON_DIR}

keyboard:
	@bin/resource.py -c keyboard -o ${DIST_DIR}/${QUEUE_DIR}/KeyboardLayouts.json

lexicon: splits-lexicon
	@bin/resource.py -c lexicon -o ${DIST_DIR}/${QUEUE_DIR}/Lexicon.json

table: splits-table
	@bin/resource.py -c table -o ${DIST_DIR}/${QUEUE_DIR}/DataTables.json

splits-table:
	@$(eval src := ${DIST_DIR}/${QUEUE_DIR}/${TABLE_DIR})
	@$(eval dst1 := ${DIST_DIR}/${GITHUB_DIR}/${TABLE_DIR})
	@$(eval dst2 := ${DIST_DIR}/${GITEE_DIR}/${TABLE_DIR})
	$(eval list := $(notdir $(wildcard ${src}/*.db)))
	@for filename in ${list}; do \
		echo $${filename} ; \
		cp ${src}/$${filename} ${dst1} ; \
		cp ${src}/$${filename} ${dst2} ; \
		bin/LoveMachine -s --2048 ${dst1}/$${filename} ;\
		bin/LoveMachine -s --1024 ${dst2}/$${filename} ;\
		rm ${dst1}/$${filename} ; \
		rm ${dst2}/$${filename} ; \
	done;

splits-lexicon:
	@$(eval src := ${DIST_DIR}/${QUEUE_DIR}/${LEXICON_DIR})
	@$(eval dst1 := ${DIST_DIR}/${GITHUB_DIR}/${LEXICON_DIR})
	@$(eval dst2 := ${DIST_DIR}/${GITEE_DIR}/${LEXICON_DIR})
	$(eval list := $(notdir $(wildcard ${src}/*.db)))
	@for filename in ${list}; do \
		echo $${filename} ; \
		cp ${src}/$${filename} ${dst1} ; \
		cp ${src}/$${filename} ${dst2} ; \
		bin/LoveMachine -s --2048 ${dst1}/$${filename} ;\
		bin/LoveMachine -s --1024 ${dst2}/$${filename} ;\
		rm ${dst1}/$${filename} ; \
		rm ${dst2}/$${filename} ; \
	done;

splits: splits-table splits-lexicon

table-db:
	$(eval excludes := \
		_sample.cin _demo.cin \
		array-shortcode.cin array-special.cin \
		boshiamy.cin liu.cin bossy.cin \
		bpmf-ext.cin \
		cj-ext.cin cj-wildcard.cin simplex-ext.cin \
		jyutping.cin jyutping-toneless.cin \
		ov_ezbig.cin ov_ezsmall.cin \
		stroke-stroke5.cin wubizixing.cin \
		egyptian.cin ehq-symbols.cin esperanto.cin \
		kk.cin kks.cin klingon.cin morse.cin telecode.cin \
	)
	$(eval all := $(notdir $(wildcard ${TABLE_DIR}/*.cin)))
	$(eval list := $(filter-out $(excludes), $(all)))

	@for filename in ${list}; do \
		if [[ -f "${TABLE_DIST_PATH}/$${filename}.db" ]]; then \
			echo "[X] $${filename}.db" ; \
		else \
			if [[ "$${filename}" =~ ^array30* ]]; then \
				bin/cin2db.py -i ${TABLE_DIR}/$${filename} -o ${TABLE_DIST_PATH}/$${filename}.db -e array ; \
			else \
				bin/cin2db.py -i ${TABLE_DIR}/$${filename} -o ${TABLE_DIST_PATH}/$${filename}.db ; \
			fi ; \
		fi ; \
	done;

lexicon-db: lexicon-array lexicon-jieba lexicon-jyutping lexicon-mcbpmf lexicon-moe

emoji-db:
	@bin/emojidb.py --update -d rawdata/emoji
	@bin/emojidb.py --run -d rawdata/emoji -o ${DIST_DIR}/emoji.db
	@echo "Test new emoji..."
	@bin/emojidb.py -test "停" -o ${DIST_DIR}/emoji.db
	@bin/emojidb.py -test "鵝" -o ${DIST_DIR}/emoji.db

unihan-db:
	@bin/unihan.py -o ${DIST_DIR}/Unihan.db

char-db:
	@bin/character.py -i ${LEXICON_DIR}/symbol.json ${DIST_DIR}/Character.db

clear:
	@echo "Clear dist"
	@-rm -fr ${DIST_DIR}/* | tqdm

dist:
	@echo "Distribute resource files...\n"
	@for file in DataTables.json KeyboardLayouts.json Lexicon.json ; do \
		if [[ -f "${DIST_DIR}/${QUEUE_DIR}/$${file}" ]]; then \
			echo "[v] $${file}" ; \
			cp ${DIST_DIR}/${QUEUE_DIR}/$${file} ${DIST_DIR}/${GITHUB_DIR}/$${file} ; \
			cp ${DIST_DIR}/${QUEUE_DIR}/$${file} ${DIST_DIR}/${GITEE_DIR}/$${file} ; \
			cp ${DIST_DIR}/${QUEUE_DIR}/$${file} ${SRC_PATH}/$${file} ; \
		else \
			echo "[404] $${file}" ; \
		fi ; \
	done;

	@for file in KeyMapping.json ; do \
		if [[ -f "./$${file}" ]]; then \
			echo "[v] $${file}" ; \
			cp $${file} ${DIST_DIR}/${GITHUB_DIR}/$${file} ; \
			cp $${file} ${DIST_DIR}/${GITEE_DIR}/$${file} ; \
			cp $${file} ${SRC_PATH}/$${file} ; \
		else \
			echo "[404] $${file}" ; \
		fi ; \
	done;

	@for file in emoji.db Character.db Unihan.db ; do \
		if [[ -f "${DIST_DIR}/$${file}" ]]; then \
			echo "[v] $${file}" ; \
			cp ${DIST_DIR}/$${file} ${SRC_PATH}/$${file} ; \
		else \
			echo "[404] $${file}" ; \
		fi ; \
	done;

lexicon-array:
	@$(eval file := $(wildcard rawdata/array30/array30-phrase*.txt))
	@mkdir -p ${LEXICON_DIST_PATH}
	@bin/txt2csv.py -i ${file} -o ${LEXICON_DIR}/array30.csv -c 3 1 0
	@bin/lexicon2db.py -i ${LEXICON_DIR}/array30.csv -o ${LEXICON_DIST_PATH}/array30.csv.db

lexicon-jieba:
	@mkdir -p ${LEXICON_DIST_PATH}
	@bin/jieba2csv.py -i rawdata/jieba/jieba/dict.txt -o ${LEXICON_DIR}/jieba.csv
	@bin/lexicon2db.py -i ${LEXICON_DIR}/jieba.csv -o ${LEXICON_DIST_PATH}/jieba.csv.db

lexicon-jyutping:
	@bin/jyutping-rime.py -i rawdata/rime-cantonese/jyut6ping3.words.dict.yaml -o ${LEXICON_DIR}/jyutping.csv -t phrase
	@bin/lexicon2db.py -i ${LEXICON_DIR}/jyutping.csv -o ${LEXICON_DIST_PATH}/jyutping.csv.db

lexicon-mcbpmf:
	@bin/mcbpmf2csv.py -i rawdata/McBopomofo/Source/Data/phrase.occ -o ${LEXICON_DIR}/mcbopomofo.csv
	@bin/lexicon2db.py -i ${LEXICON_DIR}/mcbopomofo.csv -o ${LEXICON_DIST_PATH}/mcbopomofo.csv.db

lexicon-moe:
	@bin/moe2csv.py -i rawdata/moe/concised.csv -o ${LEXICON_DIR}/moe-concised.csv
	@bin/moe2csv.py -i rawdata/moe/idioms.csv -o ${LEXICON_DIR}/moe-idioms.csv
	@bin/moe2csv.py -i rawdata/moe/revised.csv -o ${LEXICON_DIR}/moe-revised.csv
	@bin/lexicon2db.py -i ${LEXICON_DIR}/moe-concised.csv -o ${LEXICON_DIST_PATH}/moe-concised.csv.db
	@bin/lexicon2db.py -i ${LEXICON_DIR}/moe-idioms.csv -o ${LEXICON_DIST_PATH}/moe-idioms.csv.db
	@bin/lexicon2db.py -i ${LEXICON_DIR}/moe-revised.csv -o ${LEXICON_DIST_PATH}/moe-revised.csv.db

# 3rd party repo

pull:
	@echo "Upstream pulling..."
	@echo "upstream: array10"
	@cd rawdata/array10; git pull
	@echo "upstream: array30"
	@cd rawdata/array30; git pull
	@echo "upstream: ghcm"
	@cd rawdata/ghcm; git pull
	@echo "upstream: jeiba"
	@cd rawdata/jieba; git pull
	@echo "upstream: rime-cantones"
	@cd rawdata/rime-cantonese; git pull
	@echo "upstream: McBopomofo"
	@cd rawdata/McBopomofo; git pull
	@echo "upstream: tongwen"
	@cd rawdata/tongwen-core; git pull

array10:
	@echo "Update local version from upsteam..."
	@$(eval file := $(wildcard rawdata/array10/OpenVanilla/array10a*.cin))
	@cp ${file} ${TABLE_DIR}/array10a.cin
	@$(eval file := $(wildcard rawdata/array10/OpenVanilla/array10b*.cin))
	@cp ${file} ${TABLE_DIR}/array10b.cin
	@$(eval file := $(wildcard rawdata/array10/OpenVanilla/array10c*.cin))
	@cp ${file} ${TABLE_DIR}/array10c.cin
	@bin/cin2db.py -i ${TABLE_DIR}/array10a.cin -o ${TABLE_DIST_PATH}/array10a.cin.db
	@bin/cin2db.py -i ${TABLE_DIR}/array10b.cin -o ${TABLE_DIST_PATH}/array10b.cin.db
	@bin/cin2db.py -i ${TABLE_DIR}/array10c.cin -o ${TABLE_DIST_PATH}/array10c.cin.db

array30:
	@echo "Update local version from upsteam..."
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
	@bin/cin2db.py -i ${TABLE_DIR}/array30.cin -o ${TABLE_DIST_PATH}/array30.cin.db -e array
	@bin/cin2db.py -i ${TABLE_DIR}/array30-OkidoKey.cin -o ${TABLE_DIST_PATH}/array30-OkidoKey.cin.db -e array
	@bin/cin2db.py -i ${TABLE_DIR}/array30-OkidoKey-big.cin -o ${TABLE_DIST_PATH}/array30-OkidoKey-big.cin.db -e array

bossy:
	@bin/cin2db.py -i rawdata/boshiamy/boshiamy_t.cin rawdata/boshiamy/boshiamy_ct.cin rawdata/boshiamy/boshiamy_j.cin rawdata/boshiamy/hangulromaja.cin -o rawdata/boshiamy/bossy.cin.db -e bossy
	@echo "Generate CIN table..."
	@bin/db2cin.py -i rawdata/boshiamy/bossy.cin.db -o rawdata/boshiamy/bossy.cin --header rawdata/boshiamy/bossy-header.cin

bossydiff:
	@#bin/xxcin.py -m diff -i rawdata/array30/OpenVanilla/array30-OpenVanilla-big-v2023-1.0-20230211.cin -x rawdata/boshiamy/boshiamy_t.cin rawdata/boshiamy/boshiamy_c.cin rawdata/boshiamy/boshiamy_j.cin -o rawdata/boshiamy/diff-array30-big.txt
	@#bin/xxcin.py -m diff -i rawdata/array30/OkidoKey/array30-OkidoKey-regular-v2023-1.0.cin -x rawdata/boshiamy/boshiamy_t.cin rawdata/boshiamy/boshiamy_c.cin rawdata/boshiamy/boshiamy_j.cin -o rawdata/boshiamy/diff-array30-reg.txt
	@bin/xxcin.py -m diff -s a -i rawdata/array30/OkidoKey/array30-OkidoKey-regular-v2023-1.0.cin -x rawdata/boshiamy/boshiamy_t.cin rawdata/boshiamy/boshiamy_c.cin rawdata/boshiamy/boshiamy_j.cin -o tmp/diff.txt

ghcm:
	@bin/rime2cin.py -i rawdata/ghcm/SM.dict.yaml -o ${TABLE_DIR}/ghcm.cin -x rawdata/misc/ghcm-header.cin
	@bin/cin2db.py -i ${TABLE_DIR}/ghcm.cin -o ${TABLE_DIST_PATH}/ghcm.cin.db

jyutping:
	@bin/jyutping-rime.py -i rawdata/rime-cantonese/jyut6ping3.chars.dict.yaml -o ${TABLE_DIR}/jyut6ping3.cin -t tone --header rawdata/misc/jyut6ping3-header.cin
	@bin/jyutping-rime.py -i rawdata/rime-cantonese/jyut6ping3.chars.dict.yaml -o ${TABLE_DIR}/jyut6ping3-toneless.cin -t toneless --header rawdata/misc/jyut6ping3-toneless-header.cin
	@bin/cin2db.py -i ${TABLE_DIR}/jyut6ping3.cin -o ${TABLE_DIST_PATH}/jyut6ping3.cin.db
	@bin/cin2db.py -i ${TABLE_DIR}/jyut6ping3-toneless.cin -o ${TABLE_DIST_PATH}/jyut6ping3-toneless.cin.db

moe-revised:
	@$(eval version = $(notdir $(wildcard rawdata/moe/src/dict_revised_*.xlsx)))
	@$(eval version = $(shell echo '${version}' | sed 's/dict_revised_\(.*\)\.xlsx/\1/' ))
	@echo "revised: ${version}"
	@in2csv rawdata/moe/src/dict_revised_${version}.xlsx > rawdata/moe/revised-raw.csv
	@csvcut -c 字詞號,字詞名,注音一式,漢語拼音,多音參見訊息 rawdata/moe/revised-raw.csv > rawdata/moe/revised.csv
	@-rm rawdata/moe/revised-raw.csv
	@sed -i '' -e 's/編號 .* 版本/編號 ${version} 版本/g' ${LEXICON_DIR}/moe-revised.csv.txt

# original dict_idioms_2020_20230629.xls cam with incomplete fomular binding to foreign file
# must manually save as another copy to fix above question before using csvkit
moe-idioms:
	@$(eval version = $(notdir $(wildcard rawdata/moe/src/dict_idioms_*.xlsx)))
	@$(eval version = $(shell echo '${version}' | sed 's/dict_idioms_\(.*\)\.xlsx/\1/' ))
	@echo "idioms: ${version}"
	@in2csv rawdata/moe/src/dict_idioms_${version}.xlsx > rawdata/moe/idioms-raw.csv
	@csvcut -c 編號,成語,注音,漢語拼音 rawdata/moe/idioms-raw.csv > rawdata/moe/idioms.csv
	@sed -i '' -e 's/編號 .* 版本/編號 ${version} 版本/g' ${LEXICON_DIR}/moe-idioms.csv.txt
	@-rm rawdata/moe/idioms-raw.csv

moe-concised:
	@$(eval version = $(notdir $(wildcard rawdata/moe/src/dict_concised_*.xlsx)))
	@$(eval version = $(shell echo '${version}' | sed 's/dict_concised_\(.*\)\.xlsx/\1/' ))
	@echo "concised: ${version}"
	@in2csv rawdata/moe/src/dict_concised_${version}.xlsx > rawdata/moe/concised-raw.csv
	@csvcut -c 字詞號,字詞名,注音一式,漢語拼音,多音參見訊息 rawdata/moe/concised-raw.csv > rawdata/moe/concised.csv
	@-rm rawdata/moe/concised-raw.csv
	@sed -i '' -e 's/編號 .* 版本/編號 ${version} 版本/g' ${LEXICON_DIR}/moe-concised.csv.txt

moe-csv: moe-idioms moe-concised moe-revised
	@echo "General all mos csv files from xlx"

# helper

admob:
	@curl https://dl.google.com/googleadmobadssdk/googlemobileadssdkios.zip -o tmp/googlemobileadssdkios.zip
	@cd tmp; unzip -o -q googlemobileadssdkios.zip
	@$(eval dir = $(wildcard tmp/GoogleMobileAdsSdkiOS-*))
	@cd ${dir}; open .
