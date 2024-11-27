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
	@$(MISE_RUN) resource.py -c lexicon -o $(DIST_QUEUE_DIR)/Lexicon.json

array:
	@$(MISE_RUN) lexicon2db.py -i $(LEXICON_DIR)/array30.csv -o $(DIST_QUEUE_DIR)/lexicon/array30.csv.db

cedict:
	@$(MISE_RUN) lexicon2db.py -i $(LEXICON_DIR)/cedict-hant.csv -o $(DIST_QUEUE_DIR)/lexicon/cedict-hant.csv.db
	@$(MISE_RUN) lexicon2db.py -i $(LEXICON_DIR)/cedict-hans.csv -o $(DIST_QUEUE_DIR)/lexicon/cedict-hans.csv.db

jieba:
	@$(MISE_RUN) lexicon2db.py -i $(LEXICON_DIR)/jieba.csv -o $(DIST_QUEUE_DIR)/lexicon/jieba.csv.db

jyutping:
	@$(MISE_RUN) lexicon2db.py -i $(LEXICON_DIR)/jyutping.csv -o $(DIST_QUEUE_DIR)/lexicon/jyutping.csv.db

mcbpmf:
	@$(MISE_RUN) lexicon2db.py -i $(LEXICON_DIR)/mcbopomofo.csv -o $(DIST_QUEUE_DIR)/lexicon/mcbopomofo.csv.db

moe:
	@$(MISE_RUN) lexicon2db.py -i $(LEXICON_DIR)/moe-concised.csv -o $(DIST_QUEUE_DIR)/lexicon/moe-concised.csv.db
	@$(MISE_RUN) lexicon2db.py -i $(LEXICON_DIR)/moe-idioms.csv -o $(DIST_QUEUE_DIR)/lexicon/moe-idioms.csv.db
	@$(MISE_RUN) lexicon2db.py -i $(LEXICON_DIR)/moe-revised.csv -o $(DIST_QUEUE_DIR)/lexicon/moe-revised.csv.db