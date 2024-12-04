.PHONY: test table lexicon build dist init
include config.mk

define SYNOPSIS

@echo "OkidoKey/Frankie Makefile"
@echo ""

endef

usage:
	@echo $(SYNOPSIS)

test:
	@$(MISE_RUN) test.py $(BUILD_DIR)

init:
	@echo "initial env"
	@mkdir -p build/queue/table
	@mkdir -p build/queue/lexicon
	@mkdir -p dist


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
	@$(MISE_RUN) resource.py -c keyboard -o $(BUILD_QUEUE_DIR)/KeyboardLayouts.json

emoji:
	@$(MISE_RUN) emojidb.py --update -d $(RAWDATA_DIR)/emoji
	@$(MISE_RUN) emojidb.py --run -d $(RAWDATA_DIR)/emoji -o $(BUILD_DIR)/emoji.db

unihan:
	@$(MISE_RUN) unihan.py -o $(BUILD_DIR)/Unihan.db

char:
	@$(MISE_RUN) character.py -i $(LEXICON_DIR)/symbol.json $(BUILD_DIR)/Character.db

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
