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
	@mkdir -p build/gitee/table
	@mkdir -p build/gitee/lexicon
	@mkdir -p build/github/table
	@mkdir -p build/github/lexicon
	@mkdir -p dist/gitee
	@mkdir -p dist/github

clear:
	@echo "Clean up build folder..."
	@-rm build/gitee/table/*
	@-rm build/gitee/lexicon/*
	@-rm build/github/table/*
	@-rm build/github/lexicon/*

clear-all: clear
	@-rm build/queue/table/*
	@-rm build/queue/lexicon/*

all: table lexicon emoji unihan char keyboard json dist
	@echo "Buill everything"

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
	@cp -a $(BUILD_QUEUE_DIR)/*.json $(DIST_DIR)/gitee
	@cp -a $(BUILD_QUEUE_DIR)/*.json $(DIST_DIR)/github
	@cp -a $(CURDIR)/KeyMapping.json $(DIST_DIR)/gitee
	@cp -a $(CURDIR)/KeyMapping.json $(DIST_DIR)/github
	@make clear

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
