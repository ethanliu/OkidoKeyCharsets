.PHONY: usage all clear test table lexicon dist
include config.mk

define SYNOPSIS

@echo "OkidoKey/Frankie Makefile"
@echo ""

endef

usage:
	@echo $(SYNOPSIS)

test:
	@$(BIN_DIR)/run.sh test.py $(DIST_DIR)

keyboard:
	@$(BIN_DIR)/run.sh resource.py -c keyboard -o $(QUEUE_DIR)/KeyboardLayouts.json

emoji:
	@$(BIN_DIR)/run.sh emojidb.py --update -d $(RAWDATA_DIR)/emoji
	@$(BIN_DIR)/run.sh emojidb.py --run -d $(RAWDATA_DIR)/emoji -o $(DIST_DIR)/emoji.db

unihan:
	@$(BIN_DIR)/run.sh unihan.py -o $(DIST_DIR)/Unihan.db

char:
	@$(BIN_DIR)/run.sh character.py -i $(LEXICON_DIR)/symbol.json $(DIST_DIR)/Character.db

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

