.PHONY: usage clear table lexicon dist
include config.mk

define SYNOPSIS

@echo "usage..."
@echo "arg - description"

endef

usage:
	@echo $(SYNOPSIS)

clear:
	@echo "Remove dist files..."
	@-rm -fr $(DIST_GITHUB_DIR)/*
	@-rm -fr $(DIST_GITEE_DIR)/*

init:
	@mkdir -p $(DIST_GITHUB_DIR)/table
	@mkdir -p $(DIST_GITHUB_DIR)/lexicon
	@mkdir -p $(DIST_GITEE_DIR)/table
	@mkdir -p $(DIST_GITEE_DIR)/lexicon

build: init table lexicon
	@echo "Update dest: github"
	@cp -aR $(DIST_GITHUB_DIR)/* ../repo-dist/github
	@echo "Update dest: gitee"
	@cp -aR $(DIST_GITEE_DIR)/* ../repo-dist/gitee

table:
	@$(eval src := $(DIST_QUEUE_DIR)/table)
	@$(eval dst1 := $(DIST_GITHUB_DIR)/table)
	@$(eval dst2 := $(DIST_GITEE_DIR)/table)
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
	@$(eval src := $(DIST_QUEUE_DIR)/lexicon)
	@$(eval dst1 := $(DIST_GITHUB_DIR)/lexicon)
	@$(eval dst2 := $(DIST_GITEE_DIR)/lexicon)
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
