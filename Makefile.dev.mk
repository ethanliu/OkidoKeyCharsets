.PHONY: usage clear table lexicon dist

DIST_DIR := dist
QUEUE_DIR := queue
GITEE_DIR := gitee
GITHUB_DIR := github

SRC_PATH := ../src/baker/baker/Supporting\ Files/

define SYNOPSIS
@echo "usage..."
@echo "arg - description"
endef

usage:
	@echo ${SYNOPSIS}

test:
	@echo "[test]"
	@bin/cin2db.py -i table/array30-OkidoKey.cin -o tmp/array30-OkidoKey.cin.db -e array

test2holder:
	@bin/cin2db.py -i table/array30.cin -o tmp/array30.cin.db -e array
	@#bin/unihan.py -o tmp/Unihan.db > tmp/tmp.txt
	@bin/cin2db.py -i table/array30-OkidoKey-big.cin -o tmp/array30-OkidoKey-big.cin.db -e array

emoji-test:
	@echo "Test new emoji..."
	@bin/emojidb.py -test "停" -o ${DIST_DIR}/emoji.db
	@bin/emojidb.py -test "鵝" -o ${DIST_DIR}/emoji.db

sync:
	@echo "Distribute resource files...\n"
	@for file in DataTables.json KeyboardLayouts.json Lexicon.json ; do \
		if [[ -f "${DIST_DIR}/${QUEUE_DIR}/$${file}" ]]; then \
			echo "[v] $${file}" ; \
			cp ${DIST_DIR}/${QUEUE_DIR}/$${file} ${DIST_DIR}/${GITHUB_DIR}/$${file} ; \
			cp ${DIST_DIR}/${QUEUE_DIR}/$${file} ${DIST_DIR}/${GITEE_DIR}/$${file} ; \
			cp ${DIST_DIR}/${QUEUE_DIR}/$${file} ${SRC_PATH}/$${file} ; \
		else \
			echo "[404] $${file}" ; \
		fi ; \
	done;

	@for file in KeyMapping.json ; do \
		if [[ -f "./$${file}" ]]; then \
			echo "[v] $${file}" ; \
			cp $${file} ${DIST_DIR}/${GITHUB_DIR}/$${file} ; \
			cp $${file} ${DIST_DIR}/${GITEE_DIR}/$${file} ; \
			cp $${file} ${SRC_PATH}/$${file} ; \
		else \
			echo "[404] $${file}" ; \
		fi ; \
	done;

	@for file in emoji.db Character.db Unihan.db ; do \
		if [[ -f "${DIST_DIR}/$${file}" ]]; then \
			echo "[v] $${file}" ; \
			cp ${DIST_DIR}/$${file} ${SRC_PATH}/$${file} ; \
		else \
			echo "[404] $${file}" ; \
		fi ; \
	done;



define bossy_header
	$(eval _suffix = $(1))
	@cat rawdata/bossy/bossy-header.cin > "rawdata/bossy/ext/bossy-${_suffix}.cin.tmp"
	@echo "%chardef begin" >> "rawdata/bossy/ext/bossy-${_suffix}.cin.tmp"
	@cat "rawdata/bossy/ext/bossy-${_suffix}.cin" >> "rawdata/bossy/ext/bossy-${_suffix}.cin.tmp"
	@echo "%chardef end" >> "rawdata/bossy/ext/bossy-${_suffix}.cin.tmp"
	@-rm "rawdata/bossy/ext/bossy-${_suffix}.cin"
	@-mv "rawdata/bossy/ext/bossy-${_suffix}.cin.tmp" "rawdata/bossy/ext/bossy-${_suffix}.cin"
	@sed -i '' -e "s/%ename bossy/%ename bossy-${_suffix}/g" "rawdata/bossy/ext/bossy-${_suffix}.cin"
	@sed -i '' -e "s/%cname 謥蝦米/%cname 謥蝦米-${_suffix}/g" "rawdata/bossy/ext/bossy-${_suffix}.cin"
endef

bossy-cjk:
	@bin/cinkit.py rawdata/bossy/boshiamy_t.cin -m rawdata/bossy/boshiamy_ct.cin rawdata/bossy/boshiamy_j.cin rawdata/bossy/hangulromaja.cin > rawdata/bossy/ext/bossy-cjk.cin
	@$(call bossy_header, "cjk")
	@mv rawdata/bossy/ext/bossy-cjk.cin rawdata/bossy/

# depencency: bossycjk
bossy-diff:
	@bin/cinkit.py rawdata/bossy/bossy-cjk.cin -b x1 x2 > "rawdata/bossy/ext/bossy-ext.cin"
	@$(call bossy_header, "ext")
	@bin/cinkit.py rawdata/bossy/bossy-cjk.cin -b a > "rawdata/bossy/ext/bossy-a.cin"
	@$(call bossy_header, "a")

bossy-diffxfull:
	@bin/cinkit.py rawdata/bossy/bossy-cjk.cin -b b > "rawdata/bossy/ext/bossy-b.cin"
	@$(call bossy_header, "b")
	@bin/cinkit.py rawdata/bossy/bossy-cjk.cin -b c > "rawdata/bossy/ext/bossy-c.cin"
	@$(call bossy_header, "c")
	@bin/cinkit.py rawdata/bossy/bossy-cjk.cin -b d > "rawdata/bossy/ext/bossy-d.cin"
	@$(call bossy_header, "d")
	@bin/cinkit.py rawdata/bossy/bossy-cjk.cin -b e > "rawdata/bossy/ext/bossy-e.cin"
	@$(call bossy_header, "e")
	@bin/cinkit.py rawdata/bossy/bossy-cjk.cin -b f > "rawdata/bossy/ext/bossy-f.cin"
	@$(call bossy_header, "f")
	@bin/cinkit.py rawdata/bossy/bossy-cjk.cin -b g > "rawdata/bossy/ext/bossy-g.cin"
	@$(call bossy_header, "g")
	@bin/cinkit.py rawdata/bossy/bossy-cjk.cin -b h > "rawdata/bossy/ext/bossy-h.cin"
	@$(call bossy_header, "h")
	@bin/cinkit.py rawdata/bossy/bossy-cjk.cin -b i > "rawdata/bossy/ext/bossy-i.cin"
	@$(call bossy_header, "i")
	@bin/cinkit.py rawdata/bossy/bossy-cjk.cin -b x > "rawdata/bossy/ext/bossy-x.cin"
	@$(call bossy_header, "x")

bossy:
	@bin/cin2db.py -i rawdata/bossy/boshiamy_t.cin rawdata/bossy/boshiamy_j.cin rawdata/bossy/hangulromaja.cin -o ${DIST_DIR}/bossy.cin.db -e bossy
	@echo "Generate CIN table..."
	@bin/db2cin.py -i rawdata/bossy/bossy.cin.db -o ${DIST_DIR}/bossy.cin --header rawdata/bossy/bossy-header.cin

# bossydiff:
# 	@bin/xxcin.py -m diff -s a -i ${TABLE_DIR}/array30.cin -x rawdata/bossy/boshiamy_t.cin rawdata/bossy/boshiamy_c.cin rawdata/bossy/boshiamy_j.cin -o tmp/diff.txt

