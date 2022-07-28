.PHONY: usage all clean pull keyboard table db lexicon emoji

PHP := /usr/bin/env php
# BASH := /usr/bin/env bash
# MODULES := $(wildcard bin/module/mod_*.php)

define SYNOPSIS

@echo "OkidoKey Charset Makefile"
@echo ""
@echo "Resources:"
@echo "	db - Build all data table databases"
@echo "	emoji - Build Emoji databases"
@echo "	keyboard - Generate KeyboardLayouts.json"
@echo "	lexicon - Build all lexicon databases"
@echo "	table - Generate DataTables.json"
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

keyboard:
	@${PHP} bin/make.php -k

table:
	@${PHP} bin/make.php -t

db:
	@${PHP} bin/make.php -d

lexicon:
	@${PHP} bin/make.php -m

emoji:
	@$(call timeStart)
	# @bin/emoji.py --update -path tmp/emoji.db -repo rawdata/emoji
	@bin/emoji.py --run -path tmp/emoji.db -repo rawdata/emoji
	@$(call timeStop)
	cp tmp/emoji.db ../src/baker/baker/Supporting\ Files/
	@-rm tmp/emoji.db

pull: array jyutping ghcm mcbpmf ov tongwen jieba

all: keyboard table db lexicon gitee

clean:
	@echo "clean all...."

sync:
	cp DataTables.json ../src/baker/baker/Supporting\ Files/
	cp KeyMapping.json ../src/baker/baker/Supporting\ Files/
	cp KeyboardLayouts.json ../src/baker/baker/Supporting\ Files/
	cp Lexicon.json ../src/baker/baker/Supporting\ Files/

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
	@bin/moe.py -o lexicon/MoE-concised.csv rawdata/moe/concised.csv
	@bin/moe.py -o lexicon/MoE-idioms.csv rawdata/moe/idioms.csv
	@bin/moe.py -o lexicon/MoE-revised.csv rawdata/moe/revised.csv
	@-rm db/lexicon-MoE-concised.csv.db
	@-rm db/lexicon-MoE-idioms.csv.db
	@-rm db/lexicon-MoE-revised.csv.db
	@${PHP} bin/make.php -m lexicon/MoE-concised.csv lexicon/MoE-idioms.csv lexicon/MoE-revised.csv
	@$(call timeStop)

jieba:
	@cd rawdata/jieba; git pull
	@$(call timeStart)
	@-cp lexicon/Jieba-hans.csv tmp.jieba.csv
	@${PHP} bin/make.php -c jieba rawdata/jieba/jieba/dict.txt tmp.jieba.csv > lexicon/Jieba-hans.csv
	@-rm tmp.jieba.csv
	@-rm db/lexicon-Jieba-hans.csv.db
	@${PHP} bin/make.php -m lexicon/Jieba-hans.csv
	@$(call timeStop)

# jiebatest:
# 	@$(call timeStart)
# 	@-cp lexicon/Jieba-hans.csv tmp.jieba.csv
# 	@-opencc -c t2s.json -i lexicon/McBopomofo-phrase.csv -o tmp.mb.csv
# 	@${PHP} bin/make.php -c jieba rawdata/jieba/jieba/dict.txt tmp.jieba.csv tmp.mb.csv > lexicon/Jieba-hans.csv
# 	@-rm tmp.jieba.csv
# 	@-rm tmp.mb.csv
# 	@$(call timeStop)

mcbpmf:
	@cd rawdata/McBopomofo; git pull
	@$(call timeStart)
	@${PHP} bin/make.php -c mcbpmf rawdata/McBopomofo/Source/Data/BPMFMappings.txt > lexicon/McBopomofo-phrase.csv
	@-rm db/lexicon-McBopomofo-phrase.csv.db
	@${PHP} bin/make.php -m lexicon/McBopomofo-phrase.csv
	@$(call timeStop)

jyutping:
	@cd rawdata/rime-cantonese; git pull
	@$(call timeStart)
	@${PHP} bin/make.php -c jyut6ping3 rawdata/rime-cantonese/jyut6ping3.dict.yaml > table/jyut6ping3.cin
	@${PHP} bin/make.php -c jyut6ping3-toneless rawdata/rime-cantonese/jyut6ping3.dict.yaml > table/jyut6ping3-toneless.cin
	@${PHP} bin/make.php -c jyut6ping3-phrase rawdata/rime-cantonese/jyut6ping3.dict.yaml > lexicon/Rime-cantonese.csv
	@-rm db/jyut6ping3.cin.db
	@-rm db/jyut6ping3-toneless.cin.db
	@-rm db/lexicon-Rime-cantonese.csv.db
	@${PHP} bin/make.php -d table/jyut6ping3.cin table/jyut6ping3-toneless.cin
	@${PHP} bin/make.php -m lexicon/Rime-cantonese.csv
	@$(call timeStop)
	@#make db
	@#make lexicon

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
	@-rm db/lexicon-array30-phrase.csv.db
	@${PHP} bin/make.php -m lexicon/array30-phrase.csv

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

