.PHONY: test table lexicon build dist init
include config.mk

define SYNOPSIS

@echo "OkidoKey/Frankie Makefile"
@echo ""

endef

usage:
	@echo $(SYNOPSIS)

test:
	@$(BIN_DIR)/test.py $(BUILD_DIR)

dev:
	@make -f makefiles/dev.mk sync

init:
	@echo "initial env"
	@mkdir -p build/queue/table
	@mkdir -p build/queue/lexicon
	@mkdir -p rawdata
	@mkdir -p dist
	@mkdir -p tmp

clear-all: clear
	@-rm build/queue/table/*
	@-rm build/queue/lexicon/*

all: table lexicon emoji unihan char keyboard
	@echo "Build dependency..."
	@make -f makefiles/mega.mk build

	@echo "Patching..."
	@make -f makefiles/mega.mk unihan
	@make -f makefiles/mega.mk lexicon

	@make dist

keyboard:
	@$(BIN_DIR)/resource.py -c keyboard -o $(BUILD_QUEUE_DIR)/KeyboardLayouts.json

emoji:
# 	@$(BIN_DIR)/emojidb.py --update -d $(RAWDATA_DIR)/emoji
	@$(BIN_DIR)/emojidb.py --run -d $(RAWDATA_DIR)/emoji -o $(BUILD_DIR)/emoji.db

emoji-test:
	@$(BIN_DIR)/emojidb.py -test zwj -o $(BUILD_DIR)/emoji.db
	@$(BIN_DIR)/emojidb.py -test ranking -o $(BUILD_DIR)/emoji.db

unihan:
	@$(BIN_DIR)/unihan.py -o $(BUILD_DIR)/Unihan.db

char:
	@$(BIN_DIR)/character.py -i $(LEXICON_DIR)/symbol.json $(BUILD_DIR)/Character.db

table:
	@make -f makefiles/table.mk build

lexicon:
	@make -f makefiles/lexicon.mk build

dist:
	@make -f makefiles/dist.mk build
	@make -f makefiles/dev.mk sync
	@cp -a $(BUILD_QUEUE_DIR)/*.json $(DIST_DIR)/github
	@cp -a $(CURDIR)/KeyMapping.json $(DIST_DIR)/github
	@cp -a $(BUILD_QUEUE_DIR)/*.json $(DIST_DIR)/gitlab
	@cp -a $(CURDIR)/KeyMapping.json $(DIST_DIR)/gitlab

json:
	@make -f makefiles/table.mk json
	@make -f makefiles/lexicon.mk json
	@make -f makefiles/dev.mk sync

pull:
	@make -f makefiles/upstream.mk pull
	@echo "pull cedict"
	@make -f makefiles/cedict.mk pull
	@echo "pull moe"
	@make -f makefiles/moe.mk pull

update:
	@make -f makefiles/cedict.mk update
	@make -f makefiles/moe.mk update
	@make -f makefiles/upstream.mk update
# 	@make -f makefiles/array30.mk clear
	@make -f makefiles/array30.mk build
