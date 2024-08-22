.PHONY: usage clear table lexicon dist

TABLE_DIR := table
LEXICON_DIR := lexicon
DIST_DIR := dist

QUEUE_DIR := queue
GITEE_DIR := gitee
GITHUB_DIR := github

TABLE_DIST_PATH := ${DIST_DIR}/${QUEUE_DIR}/${TABLE_DIR}
LEXICON_DIST_PATH := ${DIST_DIR}/${QUEUE_DIR}/${LEXICON_DIR}

define SYNOPSIS
@echo "usage..."
@echo "arg - description"
endef

usage:
	@echo ${SYNOPSIS}

clear:
	@echo "Remove dist files..."
	@-rm -fr ${DIST_DIR}/${GITHUB_DIR}/*
	@-rm -fr ${DIST_DIR}/${GITEE_DIR}/*

init:
	@mkdir -p ${DIST_DIR}/${GITHUB_DIR}/${TABLE_DIR}
	@mkdir -p ${DIST_DIR}/${GITHUB_DIR}/${LEXICON_DIR}
	@mkdir -p ${DIST_DIR}/${GITEE_DIR}/${TABLE_DIR}
	@mkdir -p ${DIST_DIR}/${GITEE_DIR}/${LEXICON_DIR}

build: init table lexicon
	@echo "Update dest: github"
	@cp -aR ${DIST_DIR}/${GITHUB_DIR}/* ../repo-dist/${GITHUB_DIR}
	@echo "Update dest: gitee"
	@cp -aR ${DIST_DIR}/${GITEE_DIR}/* ../repo-dist/${GITEE_DIR}

table:
	@$(eval src := ${DIST_DIR}/${QUEUE_DIR}/${TABLE_DIR})
	@$(eval dst1 := ${DIST_DIR}/${GITHUB_DIR}/${TABLE_DIR})
	@$(eval dst2 := ${DIST_DIR}/${GITEE_DIR}/${TABLE_DIR})
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
	@make -f Makefile.table.mk json

lexicon:
	@$(eval src := ${DIST_DIR}/${QUEUE_DIR}/${LEXICON_DIR})
	@$(eval dst1 := ${DIST_DIR}/${GITHUB_DIR}/${LEXICON_DIR})
	@$(eval dst2 := ${DIST_DIR}/${GITEE_DIR}/${LEXICON_DIR})
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
	@make -f Makefile.lexicon.mk json
