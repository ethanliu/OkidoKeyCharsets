.PHONY: usage clear table lexicon dist build
include config.mk

define SYNOPSIS

@echo "usage..."
@echo "arg - description"

endef

usage:
	@echo $(SYNOPSIS)

clear:
	@echo "Remove dist files..."
	@-rm -fr $(BUILD_GITHUB_DIR)/*
	@-rm -fr $(BUILD_GITEE_DIR)/*

init:
	@mkdir -p $(BUILD_GITHUB_DIR)/table
	@mkdir -p $(BUILD_GITHUB_DIR)/lexicon
	@mkdir -p $(BUILD_GITEE_DIR)/table
	@mkdir -p $(BUILD_GITEE_DIR)/lexicon

build: init table lexicon
	@echo "Update dist repo: github"
	@cp -aR $(BUILD_GITHUB_DIR)/* $(DIST_DIR)/github
	@echo "Update dist repo: gitee"
	@cp -aR $(BUILD_GITEE_DIR)/* $(DIST_DIR)/gitee

table:
	@$(eval src := $(BUILD_QUEUE_DIR)/table)
	@$(eval dst1 := $(BUILD_GITHUB_DIR)/table)
	@$(eval dst2 := $(BUILD_GITEE_DIR)/table)
	$(eval list := $(notdir $(wildcard ${src}/*.db)))
	@for filename in ${list}; do \
		echo "💔 $${filename}" ; \
		cp ${src}/$${filename} ${dst1} ; \
		cp ${src}/$${filename} ${dst2} ; \
		bin/LoveMachine -s --2048 ${dst1}/$${filename} ;\
		bin/LoveMachine -s --1024 ${dst2}/$${filename} ;\
		rm ${dst1}/$${filename} ; \
		rm ${dst2}/$${filename} ; \
	done;
	@echo "Update resouce file"
	@make -f makefiles/table.mk json

lexicon:
	@$(eval src := $(BUILD_QUEUE_DIR)/lexicon)
	@$(eval dst1 := $(BUILD_GITHUB_DIR)/lexicon)
	@$(eval dst2 := $(BUILD_GITEE_DIR)/lexicon)
	$(eval list := $(notdir $(wildcard ${src}/*.db)))
	@for filename in ${list}; do \
		echo $${filename} ; \
		cp ${src}/$${filename} ${dst1} ; \
		cp ${src}/$${filename} ${dst2} ; \
		bin/LoveMachine -s --2048 ${dst1}/$${filename} ;\
		bin/LoveMachine -s --1024 ${dst2}/$${filename} ;\
		rm ${dst1}/$${filename} ; \
		rm ${dst2}/$${filename} ; \
	done;
	@echo "Update resouce file"
	@make -f makefiles/lexicon.mk json
