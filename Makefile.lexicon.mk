.PHONY: usage clear

DIST_DIR := dist
QUEUE_DIR := queue
LEXICON_DIR := lexicon
LEXICON_DIST_PATH := ${DIST_DIR}/${QUEUE_DIR}/${LEXICON_DIR}

define SYNOPSIS
@echo "usage..."
@echo "arg - description"
endef

usage:
	@echo ${SYNOPSIS}

init:
	@echo "Build lexicon"
	@mkdir -p ${DIST_DIR}/${QUEUE_DIR}/${LEXICON_DIR}

build: init array jieba jyutping mcbpmf moe

json:
	@bin/resource.py -c lexicon -o ${DIST_DIR}/${QUEUE_DIR}/Lexicon.json

array:
	@bin/lexicon2db.py -i ${LEXICON_DIR}/array30.csv -o ${LEXICON_DIST_PATH}/array30.csv.db

jieba:
	@bin/lexicon2db.py -i ${LEXICON_DIR}/jieba.csv -o ${LEXICON_DIST_PATH}/jieba.csv.db

jyutping:
	@bin/lexicon2db.py -i ${LEXICON_DIR}/jyutping.csv -o ${LEXICON_DIST_PATH}/jyutping.csv.db

mcbpmf:
	@bin/lexicon2db.py -i ${LEXICON_DIR}/mcbopomofo.csv -o ${LEXICON_DIST_PATH}/mcbopomofo.csv.db

moe:
	@bin/lexicon2db.py -i ${LEXICON_DIR}/moe-concised.csv -o ${LEXICON_DIST_PATH}/moe-concised.csv.db
	@bin/lexicon2db.py -i ${LEXICON_DIR}/moe-idioms.csv -o ${LEXICON_DIST_PATH}/moe-idioms.csv.db
	@bin/lexicon2db.py -i ${LEXICON_DIR}/moe-revised.csv -o ${LEXICON_DIST_PATH}/moe-revised.csv.db
