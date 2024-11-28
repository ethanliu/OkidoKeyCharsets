.PHONY: usage all clear test table lexicon dist
include config.mk

define SYNOPSIS

@echo "OkidoKey/Frankie Makefile"
@echo ""

endef

usage:
	@echo $(SYNOPSIS)

test:
	@$(MISE_RUN) test.py $(DIST_DIR)

keyboard:
	@$(MISE_RUN) resource.py -c keyboard -o $(QUEUE_DIR)/KeyboardLayouts.json

emoji:
	@$(MISE_RUN) emojidb.py --update -d $(RAWDATA_DIR)/emoji
	@$(MISE_RUN) emojidb.py --run -d $(RAWDATA_DIR)/emoji -o $(DIST_DIR)/emoji.db

unihan:
	@$(MISE_RUN) unihan.py -o $(DIST_DIR)/Unihan.db

char:
	@$(MISE_RUN) character.py -i $(LEXICON_DIR)/symbol.json $(DIST_DIR)/Character.db

table:
	@make -f makefiles/table.mk build

lexicon:
	@make -f makefiles/lexicon.mk build

dist:
	@make -f makefiles/dist.mk build
	@make -f makefiles/dev.mk sync

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
