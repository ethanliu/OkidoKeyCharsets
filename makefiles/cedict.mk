.PHONY: usage clear
include config.mk

# the syntax of sed in this Makefile is specified for macOS

define SYNOPSIS

@echo "Upstream :: update upstream and local repositories"
@echo "pull - find and downlad latest version from cedict"
@echo "update - update resrouce"

endef

usage:
	@echo $(SYNOPSIS)
	@echo $(TMP_DIR)

pull:
	@echo "🤝 check new version..."
	@$(MISE_RUN) cedict.py -d -o $(RAWDATA_DIR)/cedict

update:
	@$(MISE_RUN) cedict.py -i $(RAWDATA_DIR)/cedict/cedict_ts.u8 -o $(LEXICON_DIR)