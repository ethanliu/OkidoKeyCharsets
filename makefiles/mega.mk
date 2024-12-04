.PHONY: usage clear build unihan lexicon all
include config.mk

define SYNOPSIS

@echo "generate mega dict, apply weight..."
@echo "arg - description"

endef

usage:
	@echo $(SYNOPSIS)

build:
	@-rm $(TMP_DIR)/megadict.db
	@$(MISE_RUN) lexicon.py --build -i $(BUILD_QUEUE_DIR)/lexicon/*.csv.db -o $(TMP_DIR)/megadict.db

unihan:
	@$(MISE_RUN) lexicon.py --apply unihan -i $(TMP_DIR)/megadict.db -o $(BUILD_DIR)/Unihan.db

lexicon:
	@$(MISE_RUN) lexicon.py --apply lexicon -i $(TMP_DIR)/megadict.db -o $(BUILD_QUEUE_DIR)/lexicon/moe-concised.csv.db
	@$(MISE_RUN) lexicon.py --apply lexicon -i $(TMP_DIR)/megadict.db -o $(BUILD_QUEUE_DIR)/lexicon/moe-idioms.csv.db
	@$(MISE_RUN) lexicon.py --apply lexicon -i $(TMP_DIR)/megadict.db -o $(BUILD_QUEUE_DIR)/lexicon/moe-revised.csv.db
	@$(MISE_RUN) lexicon.py --apply lexicon -i $(TMP_DIR)/megadict.db -o $(BUILD_QUEUE_DIR)/lexicon/cedict-hant.csv.db
	@$(MISE_RUN) lexicon.py --apply lexicon -i $(TMP_DIR)/megadict.db -o $(BUILD_QUEUE_DIR)/lexicon/cedict-hans.csv.db
