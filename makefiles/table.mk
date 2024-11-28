.PHONY: usage clear
include config.mk

define SYNOPSIS

@echo "CIN Table"
@echo "arg - description"

endef

usage:
	@echo $(SYNOPSIS)

build:
	@mkdir -p $(DIST_QUEUE_DIR)/table
	@$(MISE_RUN) build.py -c table -t db -i $(TABLE_DIR) -o $(DIST_QUEUE_DIR)/table

json:
	@$(MISE_RUN) resource.py -c table -o $(DIST_QUEUE_DIR)/DataTables.json



