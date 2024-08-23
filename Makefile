.PHONY: usage all clear test table lexicon dist

TABLE_DIR := table
LEXICON_DIR := lexicon
DIST_DIR := dist
QUEUE_DIR := queue

define SYNOPSIS
@echo "OkidoKey/Frankie Makefile"
@echo ""
endef

usage:
	@echo ${SYNOPSIS}

keyboard:
	@bin/resource.py -c keyboard -o ${DIST_DIR}/${QUEUE_DIR}/KeyboardLayouts.json

emoji:
	@bin/emojidb.py --update -d rawdata/emoji
	@bin/emojidb.py --run -d rawdata/emoji -o ${DIST_DIR}/emoji.db

unihan:
	@bin/unihan.py -o ${DIST_DIR}/Unihan.db

char:
	@bin/character.py -i ${LEXICON_DIR}/symbol.json ${DIST_DIR}/Character.db

table:
	@make -f Makefile.table.mk build

lexicon:
	@make -f Makefile.lexicon.mk build

dist:
	@make -f Makefile.dist.mk build
	@make -f Makefile.dev.mk sync

dev:
	@make -f Makefile.table.mk json
	@make -f Makefile.lexicon.mk json
	@make -f Makefile.dev.mk sync
