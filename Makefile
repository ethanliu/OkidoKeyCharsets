.PHONY: usage all clean pull keyboard table db lexicon emoji

PHP := /usr/bin/env php
# BASH := /usr/bin/env bash
# MODULES := $(wildcard bin/module/mod_*.php)

define SYNOPSIS

@echo "OkidoKey Charset Makefile"
@echo ""
@echo "Resources:"
@echo "	db - Build all data table databases"
@echo "	emoji - Build Emoji atabases"
@echo "	keyboard - Generate KeyboardLayouts.json"
@echo "	lexicon - Build all lexicon databases"
@echo "	table - Generate DataTables.json"
@echo "Modules:"
@echo "	bossy - Merge boshiamy tables"
@echo "	ghcm - Update ghcm data table"
@echo "	gitee - Split all db files for gitee repo"
@echo "	jieba - Update Jieba lexicon"
@echo "	jyutping - Update rime-cantonese"
@echo "	mcbpmf - Update McBopomofo lexicon"
@echo "	moe - Build MoE lexicon"
@echo "	ov - Update OpenVanilla jyutping data table"
@echo ""

endef

# alternative to time cmmand

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
	@sleep 3
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
	@${PHP} bin/make.php -e

all: keyboard table db lexicon gitee

moe:
	@$(call timeStart)
	@${PHP} bin/make.php -c moe-concised rawdata/moe/dict_concised.csv > lexicon/MoE-Concised.csv
	@${PHP} bin/make.php -c moe-idoms rawdata/moe/dict_idioms.csv > lexicon/MoE-Idioms.csv
	@${PHP} bin/make.php -c moe-revised rawdata/moe/dict_revised_1.csv > lexicon/MoE-Revised.csv
	@${PHP} bin/make.php -c moe-revised rawdata/moe/dict_revised_2.csv >> lexicon/MoE-Revised.csv
	@${PHP} bin/make.php -c moe-revised rawdata/moe/dict_revised_3.csv >> lexicon/MoE-Revised.csv
	@$(call timeStop)
	@-rm db/lexicon-MoE-Concised.csv.db
	@-rm db/lexicon-MoE-Idioms.csv.db
	@-rm db/lexicon-MoE-Revised.csv.db
	@make lexicon

jieba:
	@cd rawdata/jieba; git pull
	@$(call timeStart)
	@-cp lexicon/Jieba-hans.csv tmp.jieba.csv
	@${PHP} bin/make.php -c jieba rawdata/jieba/jieba/dict.txt tmp.jieba.csv > lexicon/Jieba-hans.csv
	@-rm tmp.jieba.csv
	@$(call timeStop)
	@-rm db/lexicon-Jieba-hans.csv.db
	@make lexicon

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
	@$(call timeStop)
	@-rm db/lexicon-McBopomofo-phrase.csv.db
	@make lexicon

jyutping:
	@cd rawdata/rime-cantonese; git pull
	@$(call timeStart)
	@${PHP} bin/make.php -c jyut6ping3 rawdata/rime-cantonese/jyut6ping3.dict.yaml > table/jyut6ping3.cin
	@${PHP} bin/make.php -c jyut6ping3-toneless rawdata/rime-cantonese/jyut6ping3.dict.yaml > table/jyut6ping3-toneless.cin
	@${PHP} bin/make.php -c jyut6ping3-phrase rawdata/rime-cantonese/jyut6ping3.dict.yaml > lexicon/Rime-cantonese.csv
	@$(call timeStop)
	@-rm db/jyut6ping3.cin.db
	@-rm db/jyut6ping3-toneless.cin.db
	@-rm db/lexicon-Rime-cantonese.csv.db
	@make db
	@make lexicon

ghcm:
	@cd rawdata/ghcm; git pull
	@$(call timeStart)
	@${PHP} bin/make.php -c ghcm rawdata/ghcm/SM.dict.yaml > table/ghcm.cin
	@$(call timeStop)
	@-rm db/ghcm.cin.db
	@make db

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
	@${PHP} bin/make.php -c bossy rawdata/boshiamy/boshiamy_t.cin rawdata/boshiamy/boshiamy_j.cin rawdata/boshiamy/boshiamy_ct.cin > rawdata/boshiamy/bossy.cin
	@$(call timeStop)

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

# pull:
# 	@cd rawdata/ghcm; git pull
# 	@cd rawdata/rime-cantonese; git pull

clean:
	@echo "clean all...."