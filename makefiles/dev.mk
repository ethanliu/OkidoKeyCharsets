.PHONY: usage clear table lexicon dist
include config.mk

BOSSY_DIR := $(RAWDATA_DIR)/bossy

define SYNOPSIS

@echo "usage..."
@echo "arg - description"

endef

usage:
	@echo $(SYNOPSIS)

test:
	@$(MISE_RUN) test.py

test2holder:
	@$(MISE_RUN) cin2db.py -i table/array30.cin -o tmp/array30.cin.db -e array
	@#bin/unihan.py -o tmp/Unihan.db > tmp/tmp.txt
	@$(MISE_RUN) cin2db.py -i table/array30-OkidoKey-big.cin -o tmp/array30-OkidoKey-big.cin.db -e array

emoji-test:
	@echo "Test new emoji..."
	@$(MISE_RUN) emojidb.py -test "停" -o $(BUILD_DIR)/emoji.db
	@$(MISE_RUN) emojidb.py -test "鵝" -o $(BUILD_DIR)/emoji.db

sync:
	@echo "Distribute resource files...\n"
	@for file in DataTables.json KeyboardLayouts.json Lexicon.json ; do \
		if [[ -f "$(BUILD_QUEUE_DIR)/$${file}" ]]; then \
			echo "[v] $${file}" ; \
			cp $(BUILD_QUEUE_DIR)/$${file} $(SRC_DIR)/$${file} ; \
		else \
			echo "[404] $${file}" ; \
		fi ; \
	done;

	@for file in KeyMapping.json ; do \
		if [[ -f "./$${file}" ]]; then \
			echo "[v] $${file}" ; \
			cp $${file} $(SRC_DIR)/$${file} ; \
		else \
			echo "[404] $${file}" ; \
		fi ; \
	done;

	@for file in emoji.db Character.db Unihan.db ; do \
		if [[ -f "$(BUILD_DIR)/$${file}" ]]; then \
			echo "[v] $${file}" ; \
			cp $(BUILD_DIR)/$${file} $(SRC_DIR)/$${file} ; \
		else \
			echo "[404] $${file}" ; \
		fi ; \
	done;



define bossy_header
	$(eval _suffix = $(1))
	@cat $(BOSSY_DIR)/bossy-header.cin > "$(BOSSY_DIR)/ext/bossy-${_suffix}.cin.tmp"
	@echo "%chardef begin" >> "$(BOSSY_DIR)/ext/bossy-${_suffix}.cin.tmp"
	@cat "$(BOSSY_DIR)/ext/bossy-${_suffix}.cin" >> "$(BOSSY_DIR)/ext/bossy-${_suffix}.cin.tmp"
	@echo "%chardef end" >> "$(BOSSY_DIR)/ext/bossy-${_suffix}.cin.tmp"
	@-rm "$(BOSSY_DIR)/ext/bossy-${_suffix}.cin"
	@-mv "$(BOSSY_DIR)/ext/bossy-${_suffix}.cin.tmp" "$(BOSSY_DIR)/ext/bossy-${_suffix}.cin"
	@sed -i '' -e "s/%ename bossy/%ename bossy-${_suffix}/g" "$(BOSSY_DIR)/ext/bossy-${_suffix}.cin"
	@sed -i '' -e "s/%cname 謥蝦米/%cname 謥蝦米-${_suffix}/g" "$(BOSSY_DIR)/ext/bossy-${_suffix}.cin"
endef

bossy-cjk:
	@$(MISE_RUN) cinkit.py $(BOSSY_DIR)/boshiamy_t.cin -m $(BOSSY_DIR)/boshiamy_ct.cin $(BOSSY_DIR)/boshiamy_j.cin $(BOSSY_DIR)/hangulromaja.cin > $(BOSSY_DIR)/ext/bossy-cjk.cin
	@$(call bossy_header, "cjk")
	@mv $(BOSSY_DIR)/ext/bossy-cjk.cin $(BOSSY_DIR)/

# depencency: bossycjk
bossy-diff:
	@$(MISE_RUN) cinkit.py $(BOSSY_DIR)/bossy-cjk.cin -b x1 x2 > "$(BOSSY_DIR)/ext/bossy-ext.cin"
	@$(call bossy_header, "ext")
	@$(MISE_RUN) cinkit.py $(BOSSY_DIR)/bossy-cjk.cin -b a > "$(BOSSY_DIR)/ext/bossy-a.cin"
	@$(call bossy_header, "a")

bossy-diffxfull:
	@$(MISE_RUN) cinkit.py $(BOSSY_DIR)/bossy-cjk.cin -b b > "$(BOSSY_DIR)/ext/bossy-b.cin"
	@$(call bossy_header, "b")
	@$(MISE_RUN) cinkit.py $(BOSSY_DIR)/bossy-cjk.cin -b c > "$(BOSSY_DIR)/ext/bossy-c.cin"
	@$(call bossy_header, "c")
	@$(MISE_RUN) cinkit.py $(BOSSY_DIR)/bossy-cjk.cin -b d > "$(BOSSY_DIR)/ext/bossy-d.cin"
	@$(call bossy_header, "d")
	@$(MISE_RUN) cinkit.py $(BOSSY_DIR)/bossy-cjk.cin -b e > "$(BOSSY_DIR)/ext/bossy-e.cin"
	@$(call bossy_header, "e")
	@$(MISE_RUN) cinkit.py $(BOSSY_DIR)/bossy-cjk.cin -b f > "$(BOSSY_DIR)/ext/bossy-f.cin"
	@$(call bossy_header, "f")
	@$(MISE_RUN) cinkit.py $(BOSSY_DIR)/bossy-cjk.cin -b g > "$(BOSSY_DIR)/ext/bossy-g.cin"
	@$(call bossy_header, "g")
	@$(MISE_RUN) cinkit.py $(BOSSY_DIR)/bossy-cjk.cin -b h > "$(BOSSY_DIR)/ext/bossy-h.cin"
	@$(call bossy_header, "h")
	@$(MISE_RUN) cinkit.py $(BOSSY_DIR)/bossy-cjk.cin -b i > "$(BOSSY_DIR)/ext/bossy-i.cin"
	@$(call bossy_header, "i")
	@$(MISE_RUN) cinkit.py $(BOSSY_DIR)/bossy-cjk.cin -b x > "$(BOSSY_DIR)/ext/bossy-x.cin"
	@$(call bossy_header, "x")

bossy:
	@$(MISE_RUN) cin2db.py -i $(BOSSY_DIR)/boshiamy_t.cin $(BOSSY_DIR)/boshiamy_j.cin $(BOSSY_DIR)/hangulromaja.cin -o $(BOSSY_DIR)/bossy.cin.db -e bossy
	@echo "Generate CIN table..."
	@$(MISE_RUN) db2cin.py -i $(BOSSY_DIR)/bossy.cin.db -o $(BOSSY_DIR)/bossy.cin --header $(BOSSY_DIR)/bossy-header.cin

# bossydiff:
# 	@$(MISE_RUN) xxcin.py -m diff -s a -i ${TABLE_DIR}/array30.cin -x $(BOSSY_DIR)/boshiamy_t.cin $(BOSSY_DIR)/boshiamy_c.cin $(BOSSY_DIR)/boshiamy_j.cin -o tmp/diff.txt

