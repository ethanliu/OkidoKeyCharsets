.PHONY: usage clear table lexicon dist build
include config.mk

define SYNOPSIS

@echo "usage..."
@echo "arg - description"

endef

usage:
	@echo $(SYNOPSIS)

build: table lexicon
	@echo "Push..."
	@cp -aR $(BUILD_DIR)/github/* $(DIST_DIR)/github
	@rm -fr $(BUILD_DIR)/github
# @cp -aR $(BUILD_DIR)/gitlab/* $(DIST_DIR)/gitlab
# @rm -fr $(BUILD_DIR)/gitlab

table:
	$(call build_table,github,2048)
# $(call build_table,gitlab,2048)
	@make -f makefiles/table.mk json

lexicon:
	$(call build_lexicon,github,2048)
# $(call build_lexicon,gitlab,2048)
	@make -f makefiles/lexicon.mk json


define build_table
	$(eval name := $(1))
	$(eval size := $(2))
	$(eval list := $(notdir $(wildcard $(BUILD_QUEUE_DIR)/table/*.db)))
	@mkdir -p $(BUILD_DIR)/$(name)/table
	@for filename in ${list}; do \
		echo "💔 $${filename}" ; \
		cp $(BUILD_QUEUE_DIR)/table/$${filename} $(BUILD_DIR)/$(name)/table ; \
		$(BIN_DIR)/LoveMachine -s --$(size) $(BUILD_DIR)/$(name)/table/$${filename} ;\
		rm $(BUILD_DIR)/$(name)/table/$${filename} ; \
	done;
endef

define build_lexicon
	$(eval name := $(1))
	$(eval size := $(2))
	$(eval list := $(notdir $(wildcard $(BUILD_QUEUE_DIR)/lexicon/*.db)))
	@mkdir -p $(BUILD_DIR)/$(name)/lexicon
	@for filename in ${list}; do \
		echo "💔 $${filename}" ; \
		cp $(BUILD_QUEUE_DIR)/lexicon/$${filename} $(BUILD_DIR)/$(name)/lexicon ; \
		$(BIN_DIR)/LoveMachine -s --$(size) $(BUILD_DIR)/$(name)/lexicon/$${filename} ;\
		rm $(BUILD_DIR)/$(name)/lexicon/$${filename} ; \
	done;
endef
