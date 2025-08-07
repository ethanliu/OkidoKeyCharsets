include config.mk

.PHONY: build clear

# --- Variables for Text to Insert ---
# Using `define ... endef` and exporting for safe multi-line strings in shell commands.

define TEXT_SHORT_SPECIAL
#
# 此表格包含簡碼 (%%shortcode) 及特別碼 (%%special)
#
endef
export TEXT_SHORT_SPECIAL

define TEXT_PHRASE
# 及行列輸入法官方收錄 6 萬詞的詞庫檔
endef
export TEXT_PHRASE


build: $(TABLE_DIR)/array30.cin \
         $(TABLE_DIR)/array-special.cin \
         $(TABLE_DIR)/array-shortcode.cin \
         $(LEXICON_DIR)/array30.csv \
         $(TABLE_DIR)/array30-OkidoKey.cin \
         $(TABLE_DIR)/array30-OkidoKey-big.cin \
         $(TABLE_DIR)/array30-OkidoKey-phrase.cin \
         $(TABLE_DIR)/array30-OkidoKey-big-phrase.cin
	@echo "Patching array30 complete."
	# Clean up specific tmp files including the base copies
	@rm -f $(TMP_DIR)/array-special-processed.cin \
	       $(TMP_DIR)/array-shortcode-processed.cin \
	       $(TMP_DIR)/array30-phrase.processed \
	       $(TMP_DIR)/array30-OkidoKey.base \
	       $(TMP_DIR)/array30-OkidoKey-big.base
	@rmdir --ignore-fail-on-non-empty $(TMP_DIR) 2>/dev/null || true # Attempt to remove tmp dir if empty

# --- Core File Copying Rules (Initial Raw Copies to TABLE_DIR) ---
# These rules ensure the initial files exist in TABLE_DIR for further processing.

# Pattern rule for OpenVanilla .cin files
$(TABLE_DIR)/%.cin: $(RAWDATA_DIR)/array30/OpenVanilla/%.cin
	@mkdir -p $(@D)
	@cp $< $@

# --- Intermediate Base Copies to TMP_DIR ---
# These are the direct copies from RAWDATA_DIR that will be modified.
# They are marked as .INTERMEDIATE so Make cleans them up after use.

$(TMP_DIR)/array30-OkidoKey.base: $(RAWDATA_DIR)/array30/OkidoKey/array30-OkidoKey-regular*.cin
	@mkdir -p $(@D)
	@cp $< $@
.INTERMEDIATE: $(TMP_DIR)/array30-OkidoKey.base

$(TMP_DIR)/array30-OkidoKey-big.base: $(RAWDATA_DIR)/array30/OkidoKey/array30-OkidoKey-big*.cin
	@mkdir -p $(@D)
	@cp $< $@
.INTERMEDIATE: $(TMP_DIR)/array30-OkidoKey-big.base


# These are generated once and then appended to multiple targets.

# Processed special, keeps only charset
$(TMP_DIR)/array-special-processed.cin: $(TABLE_DIR)/array-special.cin
	@mkdir -p $(@D)
	@cat $< | sed -n '/%chardef begin/,/%chardef end/p' | sed 's/chardef/special/g' > $@
.INTERMEDIATE: $(TMP_DIR)/array-special-processed.cin

# Processed shortcode, keeps only charset
$(TMP_DIR)/array-shortcode-processed.cin: $(TABLE_DIR)/array-shortcode.cin
	@mkdir -p $(@D)
	@cat $< | sed -n '/%chardef begin/,/%chardef end/p' | sed 's/chardef/shortcode/g' > $@
.INTERMEDIATE: $(TMP_DIR)/array-shortcode-processed.cin

# Processed phrase file (filtered by tab)
$(TMP_DIR)/array30-phrase.processed: $(wildcard $(RAWDATA_DIR)/array30/array30-phrase*.txt)
	@mkdir -p $(@D)
	@echo "Filtering raw phrase file: $< -> $@"
	@grep '\t' $< > $@
.INTERMEDIATE: $(TMP_DIR)/array30-phrase.processed

$(LEXICON_DIR)/array30.csv: $(TMP_DIR)/array30-phrase.processed
	@mkdir -p $(@D)
	@echo "Converting processed phrase file to CSV: $<"
	@$(MISE_RUN) txt2csv.py -i $< -o $@ -c 3 1 0

# --- Rules for array30-OkidoKey.cin and array30-OkidoKey-big.cin ---
# These rules take the .base files (from tmp), add the shortcode/special text,
# and then append the shortcode/special content at the very end.

$(TABLE_DIR)/array30-OkidoKey.cin: $(TMP_DIR)/array30-OkidoKey.base \
                                    $(TMP_DIR)/array-shortcode-processed.cin \
                                    $(TMP_DIR)/array-special-processed.cin
	@echo "Processing $@..."
	@cp $< $@
	@TEXT_TO_INSERT="$$(echo "$$TEXT_SHORT_SPECIAL")"; \
	printf "$$TEXT_TO_INSERT\n" | sed -i '' '5r /dev/stdin' $@
	# Append processed shortcode and special block
	@cat $(TMP_DIR)/array-shortcode-processed.cin >> $@
	@cat $(TMP_DIR)/array-special-processed.cin >> $@

$(TABLE_DIR)/array30-OkidoKey-big.cin: $(TMP_DIR)/array30-OkidoKey-big.base \
                                        $(TMP_DIR)/array-shortcode-processed.cin \
                                        $(TMP_DIR)/array-special-processed.cin
	@echo "Processing $@..."
	@cp $< $@
	@TEXT_TO_INSERT="$$(echo "$$TEXT_SHORT_SPECIAL")"; \
	printf "$$TEXT_TO_INSERT\n" | sed -i '' '5r /dev/stdin' $@
	# Append processed shortcode and special block
	@cat $(TMP_DIR)/array-shortcode-processed.cin >> $@
	@cat $(TMP_DIR)/array-special-processed.cin >> $@


# --- Rules for array30-OkidoKey-phrase.cin (copy of above, then phrase content, then special/shortcode at end) ---

PHRASE_FILE := $(wildcard $(RAWDATA_DIR)/array30/array30-phrase*.txt)

$(TABLE_DIR)/array30-OkidoKey-phrase.cin: $(TMP_DIR)/array30-OkidoKey.base \
                                            $(TMP_DIR)/array30-phrase.processed \
                                            $(TMP_DIR)/array-shortcode-processed.cin \
                                            $(TMP_DIR)/array-special-processed.cin
	@echo "Generating $@..."
	@cp $< $@ # Start with the base content
	@TEXT_TO_INSERT="$$(echo "$$TEXT_SHORT_SPECIAL")"; \
	printf "$$TEXT_TO_INSERT\n" | sed -i '' '5r /dev/stdin' $@
	@TEXT_TO_INSERT="$$(echo "$$TEXT_PHRASE")"; \
	printf "$$TEXT_TO_INSERT\n" | sed -i '' '7r /dev/stdin' $@
	# Append phrase content
	@sed -i '' 's/^%chardef end/ /' $@ # Remove original end marker
	@echo "# Begin of phrase\n" >> $@
	@cat $(TMP_DIR)/array30-phrase.processed >> $@
	@echo "# End of phrase\n%chardef end\n" >> $@ # Re-add end marker
	# Append processed shortcode and special block
	@cat $(TMP_DIR)/array-shortcode-processed.cin >> $@
	@cat $(TMP_DIR)/array-special-processed.cin >> $@

$(TABLE_DIR)/array30-OkidoKey-big-phrase.cin: $(TMP_DIR)/array30-OkidoKey-big.base \
                                                $(TMP_DIR)/array30-phrase.processed \
                                                $(TMP_DIR)/array-shortcode-processed.cin \
                                                $(TMP_DIR)/array-special-processed.cin
	@echo "Generating $@..."
	@cp $< $@ # Start with the base content
	@TEXT_TO_INSERT="$$(echo "$$TEXT_SHORT_SPECIAL")"; \
	printf "$$TEXT_TO_INSERT\n" | sed -i '' '5r /dev/stdin' $@
	@TEXT_TO_INSERT="$$(echo "$$TEXT_PHRASE")"; \
	printf "$$TEXT_TO_INSERT\n" | sed -i '' '7r /dev/stdin' $@
	# Append phrase content
	@sed -i '' 's/^%chardef end/ /' $@ # Remove original end marker
	@echo "# Begin of phrase\n" >> $@
	@cat $(TMP_DIR)/array30-phrase.processed >> $@
	@echo "# End of phrase\n%chardef end\n" >> $@ # Re-add end marker
	# Append processed shortcode and special block
	@cat $(TMP_DIR)/array-shortcode-processed.cin >> $@
	@cat $(TMP_DIR)/array-special-processed.cin >> $@

clear:
	@rm $(TABLE_DIR)/array30-OkidoKey*.cin
	@rm $(LEXICON_DIR)/array30.csv