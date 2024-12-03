.PHONY: usage clear table lexicon dist
include config.mk

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
	@cat $(RAWDATA_DIR)/bossy/bossy-header.cin > "$(RAWDATA_DIR)/bossy/ext/bossy-${_suffix}.cin.tmp"
	@echo "%chardef begin" >> "$(RAWDATA_DIR)/bossy/ext/bossy-${_suffix}.cin.tmp"
	@cat "$(RAWDATA_DIR)/bossy/ext/bossy-${_suffix}.cin" >> "$(RAWDATA_DIR)/bossy/ext/bossy-${_suffix}.cin.tmp"
	@echo "%chardef end" >> "$(RAWDATA_DIR)/bossy/ext/bossy-${_suffix}.cin.tmp"
	@-rm "$(RAWDATA_DIR)/bossy/ext/bossy-${_suffix}.cin"
	@-mv "$(RAWDATA_DIR)/bossy/ext/bossy-${_suffix}.cin.tmp" "$(RAWDATA_DIR)/bossy/ext/bossy-${_suffix}.cin"
	@sed -i '' -e "s/%ename bossy/%ename bossy-${_suffix}/g" "$(RAWDATA_DIR)/bossy/ext/bossy-${_suffix}.cin"
	@sed -i '' -e "s/%cname 謥蝦米/%cname 謥蝦米-${_suffix}/g" "$(RAWDATA_DIR)/bossy/ext/bossy-${_suffix}.cin"
endef

bossy-cjk:
	@$(MISE_RUN) cinkit.py $(RAWDATA_DIR)/bossy/boshiamy_t.cin -m $(RAWDATA_DIR)/bossy/boshiamy_ct.cin $(RAWDATA_DIR)/bossy/boshiamy_j.cin $(RAWDATA_DIR)/bossy/hangulromaja.cin > $(RAWDATA_DIR)/bossy/ext/bossy-cjk.cin
	@$(call bossy_header, "cjk")
	@mv $(RAWDATA_DIR)/bossy/ext/bossy-cjk.cin $(RAWDATA_DIR)/bossy/

# depencency: bossycjk
bossy-diff:
	@$(MISE_RUN) cinkit.py $(RAWDATA_DIR)/bossy/bossy-cjk.cin -b x1 x2 > "$(RAWDATA_DIR)/bossy/ext/bossy-ext.cin"
	@$(call bossy_header, "ext")
	@$(MISE_RUN) cinkit.py $(RAWDATA_DIR)/bossy/bossy-cjk.cin -b a > "$(RAWDATA_DIR)/bossy/ext/bossy-a.cin"
	@$(call bossy_header, "a")

bossy-diffxfull:
	@$(MISE_RUN) cinkit.py $(RAWDATA_DIR)/bossy/bossy-cjk.cin -b b > "$(RAWDATA_DIR)/bossy/ext/bossy-b.cin"
	@$(call bossy_header, "b")
	@$(MISE_RUN) cinkit.py $(RAWDATA_DIR)/bossy/bossy-cjk.cin -b c > "$(RAWDATA_DIR)/bossy/ext/bossy-c.cin"
	@$(call bossy_header, "c")
	@$(MISE_RUN) cinkit.py $(RAWDATA_DIR)/bossy/bossy-cjk.cin -b d > "$(RAWDATA_DIR)/bossy/ext/bossy-d.cin"
	@$(call bossy_header, "d")
	@$(MISE_RUN) cinkit.py $(RAWDATA_DIR)/bossy/bossy-cjk.cin -b e > "$(RAWDATA_DIR)/bossy/ext/bossy-e.cin"
	@$(call bossy_header, "e")
	@$(MISE_RUN) cinkit.py $(RAWDATA_DIR)/bossy/bossy-cjk.cin -b f > "$(RAWDATA_DIR)/bossy/ext/bossy-f.cin"
	@$(call bossy_header, "f")
	@$(MISE_RUN) cinkit.py $(RAWDATA_DIR)/bossy/bossy-cjk.cin -b g > "$(RAWDATA_DIR)/bossy/ext/bossy-g.cin"
	@$(call bossy_header, "g")
	@$(MISE_RUN) cinkit.py $(RAWDATA_DIR)/bossy/bossy-cjk.cin -b h > "$(RAWDATA_DIR)/bossy/ext/bossy-h.cin"
	@$(call bossy_header, "h")
	@$(MISE_RUN) cinkit.py $(RAWDATA_DIR)/bossy/bossy-cjk.cin -b i > "$(RAWDATA_DIR)/bossy/ext/bossy-i.cin"
	@$(call bossy_header, "i")
	@$(MISE_RUN) cinkit.py $(RAWDATA_DIR)/bossy/bossy-cjk.cin -b x > "$(RAWDATA_DIR)/bossy/ext/bossy-x.cin"
	@$(call bossy_header, "x")

bossy:
	@$(MISE_RUN) cin2db.py -i $(RAWDATA_DIR)/bossy/boshiamy_t.cin $(RAWDATA_DIR)/bossy/boshiamy_j.cin $(RAWDATA_DIR)/bossy/hangulromaja.cin -o $(BUILD_DIR)/bossy.cin.db -e bossy
	@echo "Generate CIN table..."
	@$(MISE_RUN) db2cin.py -i $(RAWDATA_DIR)/bossy/bossy.cin.db -o $(BUILD_DIR)/bossy.cin --header $(RAWDATA_DIR)/bossy/bossy-header.cin

# bossydiff:
# 	@$(MISE_RUN) xxcin.py -m diff -s a -i ${TABLE_DIR}/array30.cin -x $(RAWDATA_DIR)/bossy/boshiamy_t.cin $(RAWDATA_DIR)/bossy/boshiamy_c.cin $(RAWDATA_DIR)/bossy/boshiamy_j.cin -o tmp/diff.txt

