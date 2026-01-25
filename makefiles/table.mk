.PHONY: usage clear build
include config.mk

define SYNOPSIS

@echo "CIN Table"
@echo "arg - description"

endef

usage:
	@echo $(SYNOPSIS)

build:
	@mkdir -p $(BUILD_QUEUE_DIR)/table
	@$(BIN_DIR)/build.py -c table -t db -i $(TABLE_DIR) -o $(BUILD_QUEUE_DIR)/table

json:
	@$(BIN_DIR)/resource.py -c table -o $(BUILD_QUEUE_DIR)/DataTables.json



