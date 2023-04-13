.PHONY: usage all clear test table lexicon

# SHELL := /usr/bin/env bash
SRC_PATH := ../src/baker/
MISC_PATH := ${SRC_PATH}baker/Supporting\ Files/
LITE_PATH := ${SRC_PATH}bakerlite/
GITEE_REPO_PATH := rawdata/gitee

define SYNOPSIS

@echo "OkidoKey/Frankie Makefile"
@echo ""
@echo "Resources:"
@echo "    table-db - Build all CIN table databases"
@echo "    lexicon-db - Build all lexicon databases"
@echo "    emoji-db - Build emoji.db"
@echo "    char-db - Build Character.db"
@echo "    cv-db - Build ChineseVariant.db"
@echo "    table - Generate db splits and DataTables.json"
@echo "    lexicon - Generate db splits Lexicon.json"
@echo "    keyboard - Generate KeyboardLayouts.json"
@echo "    link - Copy resources to Xcode codebase and Gitee repo"
@echo "    clear - Remove all generated files"
@echo ""
@echo "3rd party repositories:"
@echo "    pull - Update all upstream repos"
@echo "    array10 - Array10 [a/b] table builder"
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

# define lovemachine
# 	$(eval path1 := "db/$(strip ${1})")
# 	$(eval path2 := "${GITEE_REPO_PATH}/db/$(strip ${1})")
# 	@-rm ${path2}.*
# 	@cp ${path1} ${path2}
# 	@bin/LoveMachine -s ${path2}
# 	@-rm ${path2}
# endef

usage:
	@echo ${SYNOPSIS}

test:
	@$(call timeStart)
	@$(call timeStop)

table-db:
	$(eval tablePath = table)
	$(eval dbPath = db)
	$(eval excludes := \
		_sample.cin _demo.cin \
		array10a-header.cin array10b-header.cin array10c-header.cin \
		jyut6ping3-header.cin jyut6ping3-toneless-header.cin \
		ghcm-header.cin \
		array-shortcode.cin array-special.cin \
		boshiamy.cin liu.cin bossy.cin \
		bpmf-ext.cin \
		cj-ext.cin cj-wildcard.cin simplex-ext.cin \
		jyutping.cin jyutping-toneless.cin \
		ov_ezbig.cin ov_ezsmall.cin \
		stroke-stroke5.cin wubizixing.cin \
		egyptian.cin ehq-symbols.cin esperanto.cin kk.cin kks.cin klingon.cin morse.cin telecode.cin \
	)
	$(eval all := $(notdir $(wildcard ${tablePath}/*.cin)))
	$(eval list := $(filter-out $(excludes), $(all)))

	@for filename in ${list}; do \
		if [[ -f "${dbPath}/$${filename}.db" ]]; then \
			echo "[X] $${filename}.db" ; \
		else \
			if [[ "$${filename}" =~ ^array30* ]]; then \
				bin/cin2db.py -i ${tablePath}/$${filename} -o ${dbPath}/$${filename}.db --array-short ${tablePath}/array-shortcode.cin --array-special ${tablePath}/array-special.cin ; \
			else \
				bin/cin2db.py -i ${tablePath}/$${filename} -o ${dbPath}/$${filename}.db ; \
			fi ; \
		fi ; \
	done;

lexicon-db: array-phrase jieba jyutping-phrase mcbpmf moe-db
	@# update all lexicon

all-third-party-table: array10 array30 ghcm jyutping

all-third-party-lexicon: array-phrase jieba jyutping-phrase mcbpmf moe-db

all: pull all-third-party-table all-third-party-lexicon table-db lexicon-db table lexicon keyboard link
	@echo "Buil all in one command..."

clear:
	@echo "Remove all db files"
	@-rm ${GITEE_REPO_PATH}/db/*
	@-rm db/*.db | tqdm

link:
	@echo "Copy json resources files to codebase"
	@for file in DataTables.json KeyboardLayouts.json Lexicon.json KeyMapping.json ; do \
		echo "...$${file}" ; \
		cp $${file} ${MISC_PATH} ; \
		cp $${file} ${GITEE_REPO_PATH} ; \
	done;

emoji-db:
	@$(call timeStart)
	@bin/emojidb.py --update -d rawdata/emoji
	@bin/emojidb.py --run -d rawdata/emoji -o tmp/emoji.db
	@$(call timeStop)
	@echo "Test new emoji..."
	@bin/emojidb.py -test "停" -o tmp/emoji.db
	@bin/emojidb.py -test "鵝" -o tmp/emoji.db
	@echo "Copy emoji.db to src..."
	@cp tmp/emoji.db ${MISC_PATH}
	@-rm tmp/emoji.db

char-db:
	@$(call timeStart)
	@bin/character.py -i lexicon/symbol.json tmp/Character.db
	@echo "Copy Character.db to src..."
	@cp tmp/Character.db ${MISC_PATH}
	@-rm tmp/Character.db
	@$(call timeStop)

cv-db:
	@$(call timeStart)
	@bin/chinese-variant.py -i rawdata/tongwen-core/dictionaries -o tmp/ChineseVariant.db
	@echo "Copy ChineseVariant.db to src..."
	@cp tmp/ChineseVariant.db ${MISC_PATH}
	@-rm tmp/ChineseVariant.db
	@$(call timeStop)

lexicon:
	@bin/resource.py -c lexicon

keyboard:
	@bin/resource.py -c keyboard

table:
	@bin/resource.py -c table


# gitee:
# 	@$(call timeStart)
# 	$(eval REPOPATH := rawdata/gitee)

# 	@-rm ${GITEE_REPO_PATH}/db/*

# 	@for file in $(wildcard db/*.db); do \
# 		cp $$file ${GITEE_REPO_PATH}/$$file ; \
# 		bin/LoveMachine -s ${GITEE_REPO_PATH}/$$file ; \
# 		rm ${GITEE_REPO_PATH}/$$file ; \
# 	done;

# 	@bin/resource.py -c table
# 	@bin/resource.py -c lexicon

# 	@echo "Update json files..."
# 	@for file in DataTables.json KeyboardLayouts.json KeyMapping.json Lexicon.json; do \
# 		cp $$file ${GITEE_REPO_PATH} ; \
# 	done;
# 	@$(call timeStop)


# ov:
# 	@echo "Update OpenVanilla Cantonese"
# 	$(eval REPOPATH := rawdata/openvanilla)
# 	@cp table/jyut6ping3.cin ${REPOPATH}/DataTables/jyutping.cin
# 	@cp table/jyut6ping3-toneless.cin ${REPOPATH}/DataTables/jyutping-toneless.cin
# 	@sed -i '' -e 's/%ename Jyut6ping3/%ename Cantonese/g' ${REPOPATH}/DataTables/jyutping.cin
# 	@sed -i '' -e 's/%cname 粵拼/%cname 粵語拼音/g' ${REPOPATH}/DataTables/jyutping.cin
# 	@sed -i '' -e 's/%ename Jyut6ping3/%ename Cantonese/g' ${REPOPATH}/DataTables/jyutping-toneless.cin
# 	@sed -i '' -e 's/%cname 粵拼/%cname 粵語拼音/g' ${REPOPATH}/DataTables/jyutping-toneless.cin
# 	@cp ${REPOPATH}/DataTables/jyutping.cin ${REPOPATH}/Source/Mac/MacDataTables/jyutping.cin
# 	@cp ${REPOPATH}/DataTables/jyutping-toneless.cin ${REPOPATH}/Source/Mac/MacDataTables/jyutping-toneless.cin


# 3rd party

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
	@$(call timeStart)
	@echo "Update local version from upsteam..."

	@$(eval file := $(wildcard rawdata/array10/LIME/array10a*.lime))
	@bin/lime2cin.py -i ${file} -o table/array10a.cin --header table/array10a-header.cin
	@bin/cin2db.py -i table/array10a.cin -o db/array10a.cin.db

	@$(eval file := $(wildcard rawdata/array10/LIME/array10b*.lime))
	@bin/lime2cin.py -i ${file} -o table/array10b.cin --header table/array10b-header.cin
	@bin/cin2db.py -i table/array10b.cin -o db/array10b.cin.db

	@$(eval file := $(wildcard rawdata/array10/LIME/array10c*.lime))
	@bin/lime2cin.py -i ${file} -o table/array10c.cin --header table/array10c-header.cin
	@bin/cin2db.py -i table/array10c.cin -o db/array10c.cin.db

	@$(call timeStop)


array30:
	@$(call timeStart)
	@echo "Update local version from upsteam..."
	@$(eval file := $(wildcard rawdata/array30/OpenVanilla/array30*.cin))
	@cp ${file} table/array30.cin
	@$(eval file := $(wildcard rawdata/array30/OpenVanilla/array-special*.cin))
	@cp ${file} table/array-special.cin
	@$(eval file := $(wildcard rawdata/array30/OpenVanilla/array-shortcode*.cin))
	@cp ${file} table/array-shortcode.cin
	@$(eval file := $(wildcard rawdata/array30/OkidoKey/array30-OkidoKey-regular*.cin))
	@cp ${file} table/array30-OkidoKey.cin
	@$(eval file := $(wildcard rawdata/array30/OkidoKey/array30-OkidoKey-big*.cin))
	@cp ${file} table/array30-OkidoKey-big.cin
	@bin/cin2db.py -i table/array30.cin -o db/array30.cin.db --array-short table/array-shortcode.cin --array-special table/array-special.cin
	@bin/cin2db.py -i table/array30-OkidoKey.cin -o db/array30-OkidoKey.cin.db --array-short table/array-shortcode.cin --array-special table/array-special.cin
	@bin/cin2db.py -i table/array30-OkidoKey-big.cin -o db/array30-OkidoKey-big.cin.db --array-short table/array-shortcode.cin --array-special table/array-special.cin
	@$(call timeStop)

array-phrase:
	@$(eval file := $(wildcard rawdata/array30/array30-phrase*.txt))
	@bin/txt2csv.py -i ${file} -o lexicon/array30-phrase.csv -c 3 1 0
	@bin/lexicon2db.py -i lexicon/array30-phrase.csv -o db/lexicon-array30-phrase.csv.db

bossy:
	@$(call timeStart)
	@bin/cin2db.py -i rawdata/boshiamy/boshiamy_t.cin rawdata/boshiamy/boshiamy_ct.cin rawdata/boshiamy/boshiamy_j.cin rawdata/boshiamy/hangulromaja.cin -o rawdata/boshiamy/bossy.cin.db
	@echo "Generate CIN table..."
	@bin/db2cin.py -i rawdata/boshiamy/bossy.cin.db -o rawdata/boshiamy/bossy.cin --header rawdata/boshiamy/bossy-header.cin
	@$(call timeStop)

bossydiff:
	@$(call timeStart)
	@#bin/xxcin.py -m diff -i rawdata/array30/OpenVanilla/array30-OpenVanilla-big-v2023-1.0-20230211.cin -x rawdata/boshiamy/boshiamy_t.cin rawdata/boshiamy/boshiamy_c.cin rawdata/boshiamy/boshiamy_j.cin -o rawdata/boshiamy/diff-array30-big.txt
	@#bin/xxcin.py -m diff -i rawdata/array30/OkidoKey/array30-OkidoKey-regular-v2023-1.0.cin -x rawdata/boshiamy/boshiamy_t.cin rawdata/boshiamy/boshiamy_c.cin rawdata/boshiamy/boshiamy_j.cin -o rawdata/boshiamy/diff-array30-reg.txt
	@bin/xxcin.py -m diff -s a -i rawdata/array30/OkidoKey/array30-OkidoKey-regular-v2023-1.0.cin -x rawdata/boshiamy/boshiamy_t.cin rawdata/boshiamy/boshiamy_c.cin rawdata/boshiamy/boshiamy_j.cin -o tmp/diff.txt
	@$(call timeStop)

ghcm:
	@$(call timeStart)
	@bin/rime2cin.py -i rawdata/ghcm/SM.dict.yaml -o table/ghcm.cin -x table/ghcm-header.cin
	@bin/cin2db.py -i table/ghcm.cin -o db/ghcm.cin.db
	@$(call timeStop)

jieba:
	@$(call timeStart)
	@bin/jieba2csv.py -i rawdata/jieba/jieba/dict.txt -o lexicon/Jieba-hans.csv
	@bin/lexicon2db.py -i lexicon/Jieba-hans.csv -o db/lexicon-Jieba-hans.csv.db
	@$(call timeStop)

jyutping:
	@$(call timeStart)
	@bin/jyutping-rime.py -i rawdata/rime-cantonese/jyut6ping3.chars.dict.yaml -o table/jyut6ping3.cin -t tone --header table/jyut6ping3-header.cin
	@bin/jyutping-rime.py -i rawdata/rime-cantonese/jyut6ping3.chars.dict.yaml -o table/jyut6ping3-toneless.cin -t toneless --header table/jyut6ping3-toneless-header.cin
	@bin/cin2db.py -i table/jyut6ping3.cin -o db/jyut6ping3.cin.db
	@bin/cin2db.py -i table/jyut6ping3-toneless.cin -o db/jyut6ping3-toneless.cin.db
	@$(call timeStop)

jyutping-phrase:
	@$(call timeStart)
	@bin/jyutping-rime.py -i rawdata/rime-cantonese/jyut6ping3.words.dict.yaml -o lexicon/Rime-cantonese.csv -t phrase
	@bin/lexicon2db.py -i lexicon/Rime-cantonese.csv -o db/lexicon-Rime-cantonese.csv.db
	@$(call timeStop)

mcbpmf:
	@$(call timeStart)
	@bin/mcbpmf2csv.py -i rawdata/McBopomofo/Source/Data/BPMFMappings.txt -o lexicon/McBopomofo-phrase.csv
	@bin/lexicon2db.py -i lexicon/McBopomofo-phrase.csv -o db/lexicon-McBopomofo-phrase.csv.db
	@$(call timeStop)

moe-csv:
	@$(call timeStart)

	@$(eval version = $(notdir $(wildcard rawdata/moe/src/dict_revised_*_1.xls)))
	@$(eval version = $(shell echo '${version}' | sed 's/dict_revised_\(.*\)_1\.xls/\1/' ))
	@echo "Convert: revised ${version}..."
	@in2csv rawdata/moe/src/dict_revised_${version}_1.xls > rawdata/moe/revised1-raw.csv
	@in2csv rawdata/moe/src/dict_revised_${version}_2.xls > rawdata/moe/revised2-raw.csv
	@in2csv rawdata/moe/src/dict_revised_${version}_3.xls > rawdata/moe/revised3-raw.csv
	@csvstack rawdata/moe/revised1-raw.csv rawdata/moe/revised2-raw.csv rawdata/moe/revised3-raw.csv > rawdata/moe/revised-raw.csv
	@csvcut -c 字詞號,字詞名,注音一式,漢語拼音,多音參見訊息 rawdata/moe/revised-raw.csv > rawdata/moe/revised.csv
	@-rm rawdata/moe/revised-raw.csv
	@-rm rawdata/moe/revised1-raw.csv
	@-rm rawdata/moe/revised2-raw.csv
	@-rm rawdata/moe/revised3-raw.csv
	@sed -i '' -e 's/編號 .* 版本/編號 ${version} 版本/g' lexicon/MoE-revised.csv.txt

	@$(eval version = $(notdir $(wildcard rawdata/moe/src/dict_idioms_*.xls)))
	@$(eval version = $(shell echo '${version}' | sed 's/dict_idioms_\(.*\)\.xls/\1/' ))
	@echo "Convert: idioms ${version}..."
	@in2csv rawdata/moe/src/dict_idioms_${version}.xls > rawdata/moe/idioms-raw.csv
	@csvcut -c 編號,成語,注音,漢語拼音 rawdata/moe/idioms-raw.csv > rawdata/moe/idioms.csv
	@sed -i '' -e 's/編號 .* 版本/編號 ${version} 版本/g' lexicon/MoE-idioms.csv.txt
	@-rm rawdata/moe/idioms-raw.csv

	@$(eval version = $(notdir $(wildcard rawdata/moe/src/dict_concised_*.xls)))
	@$(eval version = $(shell echo '${version}' | sed 's/dict_concised_\(.*\)\.xls/\1/' ))
	@echo "Convert: concised ${version}..."
	@in2csv rawdata/moe/src/dict_concised_${version}.xls > rawdata/moe/concised-raw.csv
	@csvcut -c 字詞號,字詞名,注音一式,漢語拼音,多音參見訊息 rawdata/moe/concised-raw.csv > rawdata/moe/concised.csv
	@-rm rawdata/moe/concised-raw.csv
	@sed -i '' -e 's/編號 .* 版本/編號 ${version} 版本/g' lexicon/MoE-concised.csv.txt

	@$(call timeStop)

moe-db:
	@$(call timeStart)
	@bin/moe2csv.py -i rawdata/moe/concised.csv -o lexicon/MoE-concised.csv
	@bin/moe2csv.py -i rawdata/moe/idioms.csv -o lexicon/MoE-idioms.csv
	@bin/moe2csv.py -i rawdata/moe/revised.csv -o lexicon/MoE-revised.csv
	@bin/lexicon2db.py -i lexicon/MoE-concised.csv -o db/lexicon-MoE-concised.csv.db
	@bin/lexicon2db.py -i lexicon/MoE-idioms.csv -o db/lexicon-MoE-idioms.csv.db
	@bin/lexicon2db.py -i lexicon/MoE-revised.csv -o db/lexicon-MoE-revised.csv.db
	@$(call timeStop)

 admob:
	@$(call timeStart)
	@curl https://dl.google.com/googleadmobadssdk/googlemobileadssdkios.zip -o tmp/googlemobileadssdkios.zip
	@cd tmp; unzip -o -q googlemobileadssdkios.zip
	@$(eval dir = $(wildcard tmp/GoogleMobileAdsSdkiOS-*))
	@#echo "AdMob: ${dir}"
	@#echo "SRC: ${LITE_PATH}"
	@cd ${dir}; open .
	@$(call timeStop)
