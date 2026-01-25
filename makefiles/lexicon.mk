.PHONY: usage clear build
include config.mk

define SYNOPSIS

@echo "usage..."
@echo "arg - description"

endef

usage:
	@echo $(SYNOPSIS)

init:
	@echo "Build lexicon"
	@mkdir -p $(BUILD_QUEUE_DIR)/lexicon

build: init cedict moe jieba jyutping mcbpmf moe2

json:
	@$(BIN_DIR)/resource.py -c lexicon -o $(BUILD_QUEUE_DIR)/Lexicon.json

# array:
# 	@$(BIN_DIR)/lexicon2db.py -i $(LEXICON_DIR)/array30.csv -o $(BUILD_QUEUE_DIR)/lexicon/array30.csv.db

cedict:
	@$(BIN_DIR)/lexicon2db.py -i $(LEXICON_DIR)/cedict-hant.csv -o $(BUILD_QUEUE_DIR)/lexicon/cedict-hant.csv.db
	@$(BIN_DIR)/lexicon2db.py -i $(LEXICON_DIR)/cedict-hans.csv -o $(BUILD_QUEUE_DIR)/lexicon/cedict-hans.csv.db

jieba:
	@$(BIN_DIR)/lexicon2db.py -i $(LEXICON_DIR)/jieba.csv -o $(BUILD_QUEUE_DIR)/lexicon/jieba.csv.db

jyutping:
	@$(BIN_DIR)/lexicon2db.py -i $(LEXICON_DIR)/jyutping.csv -o $(BUILD_QUEUE_DIR)/lexicon/jyutping.csv.db

mcbpmf:
	@$(BIN_DIR)/lexicon2db.py -i $(LEXICON_DIR)/mcbopomofo.csv -o $(BUILD_QUEUE_DIR)/lexicon/mcbopomofo.csv.db

moe:
	@$(BIN_DIR)/lexicon2db.py -i $(LEXICON_DIR)/moe-concised.csv -o $(BUILD_QUEUE_DIR)/lexicon/moe-concised.csv.db
	@$(BIN_DIR)/lexicon2db.py -i $(LEXICON_DIR)/moe-idioms.csv -o $(BUILD_QUEUE_DIR)/lexicon/moe-idioms.csv.db
	@$(BIN_DIR)/lexicon2db.py -i $(LEXICON_DIR)/moe-revised.csv -o $(BUILD_QUEUE_DIR)/lexicon/moe-revised.csv.db

moe2:
	@$(BIN_DIR)/lexicon2db.py -i $(LEXICON_DIR)/moe-sutian.csv -o $(BUILD_QUEUE_DIR)/lexicon/moe-sutian.csv.db
	@$(BIN_DIR)/lexicon2db.py -i $(LEXICON_DIR)/moe-hakka.csv -o $(BUILD_QUEUE_DIR)/lexicon/moe-hakka.csv.db
