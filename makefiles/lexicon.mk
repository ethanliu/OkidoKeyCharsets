.PHONY: usage clear
include config.mk

define SYNOPSIS

@echo "usage..."
@echo "arg - description"

endef

usage:
	@echo $(SYNOPSIS)

init:
	@echo "Build lexicon"
	@mkdir -p $(DIST_QUEUE_DIR)/lexicon

build: init array jieba jyutping mcbpmf moe

json:
	@$(BIN_DIR)/run.sh resource.py -c lexicon -o $(DIST_QUEUE_DIR)/Lexicon.json

array:
	@$(BIN_DIR)/run.sh lexicon2db.py -i $(LEXICON_DIR)/array30.csv -o $(DIST_QUEUE_DIR)/lexicon/array30.csv.db

jieba:
	@$(BIN_DIR)/run.sh lexicon2db.py -i $(LEXICON_DIR)/jieba.csv -o $(DIST_QUEUE_DIR)/lexicon/jieba.csv.db

jyutping:
	@$(BIN_DIR)/run.sh lexicon2db.py -i $(LEXICON_DIR)/jyutping.csv -o $(DIST_QUEUE_DIR)/lexicon/jyutping.csv.db

mcbpmf:
	@$(BIN_DIR)/run.sh lexicon2db.py -i $(LEXICON_DIR)/mcbopomofo.csv -o $(DIST_QUEUE_DIR)/lexicon/mcbopomofo.csv.db

moe:
	@$(BIN_DIR)/run.sh lexicon2db.py -i $(LEXICON_DIR)/moe-concised.csv -o $(DIST_QUEUE_DIR)/lexicon/moe-concised.csv.db
	@$(BIN_DIR)/run.sh lexicon2db.py -i $(LEXICON_DIR)/moe-idioms.csv -o $(DIST_QUEUE_DIR)/lexicon/moe-idioms.csv.db
	@$(BIN_DIR)/run.sh lexicon2db.py -i $(LEXICON_DIR)/moe-revised.csv -o $(DIST_QUEUE_DIR)/lexicon/moe-revised.csv.db
