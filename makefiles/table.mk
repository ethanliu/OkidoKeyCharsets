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
	@$(BIN_DIR)/run.sh build.py -c table -t db -i table -o $(DIST_QUEUE_DIR)/table

json:
	@$(BIN_DIR)/run.sh resource.py -c table -o $(DIST_QUEUE_DIR)/DataTables.json



