.PHONY: usage clear

TABLE_DIR := table
DIST_DIR := dist
QUEUE_DIR := queue

define SYNOPSIS
@echo "CIN Table"
@echo "arg - description"
endef

usage:
	@echo ${SYNOPSIS}

build:
	@mkdir -p ${DIST_DIR}/${QUEUE_DIR}/${TABLE_DIR}
	@bin/build.py -c table -t db -i table -o ${DIST_DIR}/${QUEUE_DIR}/${TABLE_DIR}

json:
	@bin/resource.py -c table -o ${DIST_DIR}/${QUEUE_DIR}/DataTables.json



