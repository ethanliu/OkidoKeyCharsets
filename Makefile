.PHONY: usage all clean test

PHP := /usr/bin/env php
# SHELL := /usr/bin/env bash
# MODULES := $(wildcard bin/module/mod_*.php)
SRCPATH := ../src/baker/baker/Supporting\ Files/

define SYNOPSIS

@echo "OkidoKey Charset Makefile"
@echo ""
@echo "Resources:"
@echo "	db - Build all data table databases"
@echo "	keyboard - Generate KeyboardLayouts.json"
@echo "	lexicon - Build all lexicon databases"
@echo "	table - Generate DataTables.json"
@echo "	emoji - Build emoji.db"
@echo "	char - Build Character.db"
@echo "Modules:"
@echo "	array10 - Update Array10"
@echo "	array30 - Update Array30"
@echo "	bossy - Build custom boshiamy table"
@echo "	ghcm - Update ghcm data table"
@echo "	gitee - Split all db files for Gitee repo"
@echo "	jieba - Update Jieba lexicon"
@echo "	jyutping - Update rime-cantonese"
@echo "	mcbpmf - Update McBopomofo lexicon"
@echo "	moecsv - Convert CSV from XLS"
@echo "	moe - Build MoE lexicon"
@echo "	ov - Update OpenVanilla jyutping data table"
@echo ""

endef

# alternative to time command

define timeStart
	@date +%s > tmp.timestamp
endef

define timeStop
	@echo "\n---\nDuration: $$(($$(date +%s)-$$(cat tmp.timestamp))) seconds.\n---\n"
	@-rm tmp.timestamp
endef

usage:
	@echo ${SYNOPSIS}

test:
	@$(call timeStart)
	@$(call timeStop)


alltabledb:
	$(eval tablePath = tmp/table)
	$(eval dbPath = tmp/db)
	$(eval excludes := \
		_sample.cin \
		_demo.cin \
		array-shortcode.cin \
		array-special.cin \
		array10a-header.cin \
		array10b-header.cin \
		array30_OkidoKey-big.cin \
		bpmf-ext.cin \
		cj-ext.cin \
		cj-wildcard.cin \
		egyptian.cin \
		ehq-symbols.cin \
		esperanto.cin \
		jyutping.cin \
		jyutping-toneless.cin \
		kk.cin \
		kks.cin \
		klingon.cin \
		ov_ezbig.cin \
		ov_ezsmall.cin \
		simplex-ext.cin \
		stroke-stroke5.cin \
		morse.cin \
		telecode.cin \
	)
	$(eval all := $(notdir $(wildcard ${tablePath}/*.cin)))
	$(eval list := $(filter-out $(excludes), $(all)))

	@for filename in ${list}; do \
		if [[ -f "${dbPath}/$${filename}.db" ]]; then \
			echo "[exists] $${filename}.db"; \
		else \
			if [ $$filename == "array30.cin" ] || [ $$filename == "array30_OkidoKey.cin" ]; then \
				bin/cin2db.py -i ${tablePath}/$${filename} -o ${dbPath}/$${filename}.db --array-short ${tablePath}/array-shortcode.cin --array-special ${tablePath}/array-special.cin ; \
			else \
				bin/cin2db.py -i ${tablePath}/$${filename} -o ${dbPath}/$${filename}.db; \
			fi \
		fi \
	done;


keyboard:
	@${PHP} bin/make.php -k

table:
	@${PHP} bin/make.php -t

db:
	@${PHP} bin/make.php -d

lexicon:
	@echo "update syntax"

# pull: array jyutping ghcm mcbpmf ov tongwen jieba

all: keyboard table db lexicon gitee sync

clean:
	@echo "clean all...."

sync:
	cp DataTables.json ${SRCPATH}
	cp KeyMapping.json ${SRCPATH}
	cp KeyboardLayouts.json ${SRCPATH}
	cp Lexicon.json ${SRCPATH}

emoji:
	@$(call timeStart)
	@bin/emoji.py --update -d rawdata/emoji
	@bin/emoji.py --run -d rawdata/emoji -o tmp/emoji.db
	@$(call timeStop)
	@echo "Copy emoji.db to src..."
	@cp tmp/emoji.db ${SRCPATH}
	@-rm tmp/emoji.db

char:
	@$(call timeStart)
	@bin/character.py -i lexicon/symbol.json tmp/Character.db
	@echo "Copy Character.db to src..."
	@cp tmp/Character.db ${SRCPATH}
	@$(call timeStop)

moecsv:
	@$(call timeStart)
	$(eval version := 2015_20210330)
	@echo "Convert: revised ${version}..."
	@in2csv rawdata/moe/src/dict_revised_${version}/dict_revised_${version}_1.xls > rawdata/moe/revised1-raw.csv
	@in2csv rawdata/moe/src/dict_revised_${version}/dict_revised_${version}_2.xls > rawdata/moe/revised2-raw.csv
	@in2csv rawdata/moe/src/dict_revised_${version}/dict_revised_${version}_3.xls > rawdata/moe/revised3-raw.csv
	@csvstack rawdata/moe/revised1-raw.csv rawdata/moe/revised2-raw.csv rawdata/moe/revised3-raw.csv > rawdata/moe/revised-raw.csv
	@csvcut -c 字詞號,字詞名,注音一式,漢語拼音,多音參見訊息 rawdata/moe/revised-raw.csv > rawdata/moe/revised.csv
	@-rm rawdata/moe/revised-raw.csv
	@-rm rawdata/moe/revised1-raw.csv
	@-rm rawdata/moe/revised2-raw.csv
	@-rm rawdata/moe/revised3-raw.csv
	@sed -i '' -e 's/編號 .* 版本/編號 ${version} 版本/g' lexicon/MoE-revised.csv.txt

	$(eval version := 2020_20210329)
	@echo "Convert: idioms ${version}..."
	@in2csv rawdata/moe/src/dict_idioms_${version}.xls > rawdata/moe/idioms-raw.csv
	@csvcut -c 編號,成語,注音,漢語拼音 rawdata/moe/idioms-raw.csv > rawdata/moe/idioms.csv
	@sed -i '' -e 's/編號 .* 版本/編號 ${version} 版本/g' lexicon/MoE-idioms.csv.txt
	@-rm rawdata/moe/idioms-raw.csv

	$(eval version := 2014_20210329)
	@echo "Convert: concised ${version}..."
	@in2csv rawdata/moe/src/dict_concised_${version}.xls > rawdata/moe/concised-raw.csv
	@csvcut -c 字詞號,字詞名,注音一式,漢語拼音,多音參見訊息 rawdata/moe/concised-raw.csv > rawdata/moe/concised.csv
	@-rm rawdata/moe/concised-raw.csv
	@sed -i '' -e 's/編號 .* 版本/編號 ${version} 版本/g' lexicon/MoE-concised.csv.txt
	@$(call timeStop)

moe:
	@$(call timeStart)
	@bin/moe2csv.py -i rawdata/moe/concised.csv -o lexicon/MoE-concised.csv
	@bin/moe2csv.py -i rawdata/moe/idioms.csv -o lexicon/MoE-idioms.csv
	@bin/moe2csv.py -i rawdata/moe/revised.csv -o lexicon/MoE-revised.csv
	@bin/lexicon2db.py -i lexicon/MoE-concised.csv -o db/lexicon-MoE-concised.csv.db
	@bin/lexicon2db.py -i lexicon/MoE-idioms.csv -o db/lexicon-MoE-idioms.csv.db
	@bin/lexicon2db.py -i lexicon/MoE-revised.csv -o db/lexicon-MoE-revised.csv.db
	@$(call timeStop)

jieba:
	@cd rawdata/jieba; git pull
	@$(call timeStart)
	@bin/jieba2csv.py -i rawdata/jieba/jieba/dict.txt -o lexicon/Jieba-hans.csv
	@bin/lexicon2db.py -i lexicon/Jieba-hans.csv -o db/lexicon-Jieba-hans.csv.db
	@$(call timeStop)

mcbpmf:
	@cd rawdata/McBopomofo; git pull
	@$(call timeStart)
	@bin/mcbpmf2csv.py -i rawdata/McBopomofo/Source/Data/BPMFMappings.txt -o lexicon/McBopomofo-phrase.csv
	@bin/lexicon2db.py -i lexicon/McBopomofo-phrase.csv -o db/lexicon-McBopomofo-phrase.csv.db
	@$(call timeStop)

jyutping:
	# @cd rawdata/rime-cantonese; git pull
	@$(call timeStart)
	@bin/jyutping-rime.py -i rawdata/rime-cantonese/jyut6ping3.chars.dict.yaml -o table/jyut6ping3.cin -t tone --header table/jyut6ping3-header.cin
	@bin/jyutping-rime.py -i rawdata/rime-cantonese/jyut6ping3.chars.dict.yaml -o table/jyut6ping3-toneless.cin -t toneless --header table/jyut6ping3-toneless-header.cin
	@bin/jyutping-rime.py -i rawdata/rime-cantonese/jyut6ping3.words.dict.yaml -o table/Rime-cantonese.csv -t phrase
	@bin/cin2db.py -i table/jyut6ping3.cin -o db/jyut6ping3.cin.db
	@bin/cin2db.py -i table/jyut6ping3-toneless.cin -o db/jyut6ping3-toneless.cin.db
	@bin/lexicon2db.py -i lexicon/Rime-cantonese.csv -o db/lexicon-Rime-cantonese.csv.db
	@$(call timeStop)

ghcm:
	@cd rawdata/ghcm; git pull
	@$(call timeStart)
	@${PHP} bin/make.php -c ghcm rawdata/ghcm/SM.dict.yaml > table/ghcm.cin
	@-rm db/ghcm.cin.db
	@${PHP} bin/make.php -d table/ghcm.cin
	@$(call timeStop)

gitee:
	@$(call timeStart)
	$(eval REPOPATH := rawdata/gitee)

	@-rm ${REPOPATH}/db/*

	@for file in $(wildcard db/*.db); do \
		cp $$file ${REPOPATH}/$$file ; \
		bin/LoveMachine -s ${REPOPATH}/$$file ; \
		rm ${REPOPATH}/$$file ; \
	done;

	@${PHP} bin/make.php -c gitee DataTables.json ${REPOPATH}
	@${PHP} bin/make.php -c gitee Lexicon.json ${REPOPATH}

	@echo "Update json files..."
	@for file in DataTables.json KeyboardLayouts.json KeyMapping.json Lexicon.json; do \
		cp $$file ${REPOPATH} ; \
	done;
	@$(call timeStop)

bossy:
	@$(call timeStart)
	@${PHP} bin/make.php -c bossy rawdata/boshiamy/boshiamy_t.cin rawdata/boshiamy/boshiamy_ct.cin rawdata/boshiamy/boshiamy_j.cin rawdata/boshiamy/hangulromaja.cin > rawdata/boshiamy/bossy.cin
	@$(call timeStop)

array10:
	@cd rawdata/array10; git pull
	@$(call timeStart)
	@bin/lime2cin.py -H table/array10a-header.cin -O table/array10a.cin rawdata/array10/LIME/array10a-20220321.lime
	@bin/lime2cin.py -H table/array10b-header.cin -O table/array10b.cin rawdata/array10/LIME/array10b-20220321.lime
	@-rm db/array10a.cin.db
	@-rm db/array10b.cin.db
	@${PHP} bin/make.php -d table/array10a.cin
	@${PHP} bin/make.php -d table/array10b.cin
	@$(call timeStop)

array30:
	@cd rawdata/array30; git pull
	@$(call timeStart)
	@${PHP} bin/make.php -c array rawdata/array30
	@-rm db/array30.cin.db
	@-rm db/array30_OkidoKey.cin.db
	@${PHP} bin/make.php -d table/array30.cin
	@${PHP} bin/make.php -d table/array30_OkidoKey.cin
	@$(call timeStop)

array-phrase:
	@${PHP} bin/make.php -c array-phrase rawdata/array30/array30-phrase-20210725.txt > lexicon/array30-phrase.csv
	@bin/lexicon2db.py -i lexicon/array30-phrase.csv -o db/lexicon-array30-phrase.csv.db


ov:
	@echo "Update OpenVanilla Cantonese"
	$(eval REPOPATH := rawdata/openvanilla)
	@cp table/jyut6ping3.cin ${REPOPATH}/DataTables/jyutping.cin
	@cp table/jyut6ping3-toneless.cin ${REPOPATH}/DataTables/jyutping-toneless.cin
	@sed -i '' -e 's/%ename Jyut6ping3/%ename Cantonese/g' ${REPOPATH}/DataTables/jyutping.cin
	@sed -i '' -e 's/%cname 粵拼/%cname 粵語拼音/g' ${REPOPATH}/DataTables/jyutping.cin
	@sed -i '' -e 's/%ename Jyut6ping3/%ename Cantonese/g' ${REPOPATH}/DataTables/jyutping-toneless.cin
	@sed -i '' -e 's/%cname 粵拼/%cname 粵語拼音/g' ${REPOPATH}/DataTables/jyutping-toneless.cin
	@cp ${REPOPATH}/DataTables/jyutping.cin ${REPOPATH}/Source/Mac/MacDataTables/jyutping.cin
	@cp ${REPOPATH}/DataTables/jyutping-toneless.cin ${REPOPATH}/Source/Mac/MacDataTables/jyutping-toneless.cin

tongwen:
	@cd rawdata/tongwen-core; git pull
	@$(call timeStart)
	@${PHP} bin/make.php -c tongwen rawdata/tongwen-core/dictionaries ChineseVariant.db
	@$(call timeStop)

