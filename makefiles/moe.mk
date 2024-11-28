.PHONY: usage clear
include config.mk

# the syntax of sed in this Makefile is specified for macOS

define SYNOPSIS

@echo "Upstream :: update upstream and local repositories"
@echo "pull - find and downlad latest version from MoE"
@echo "update - update resrouce"

endef

usage:
	@echo $(SYNOPSIS)
	@echo $(TMP_DIR)

update: idioms revised concised-csv

pull:
	@echo "🤝 Checking version..."
	@$(MISE_RUN) moe2csv.py -d -o $(RAWDATA_DIR)/moe/src
# @$(MISE_RUN) moe-spider.py $(RAWDATA_DIR)/moe/src

revised:
	@$(eval version = $(notdir $(wildcard $(RAWDATA_DIR)/moe/dict_revised_*.xlsx)))
	@$(eval version = $(shell echo '${version}' | sed 's/dict_revised_\(.*\)\.xlsx/\1/' ))
	@echo "revised: ${version}"
	@sed -i '' -e 's/本詞庫來源版本：.*\n/本詞庫來源版本：${version}\n/g' $(LEXICON_DIR)/moe-revised.csv.txt
	@in2csv $(RAWDATA_DIR)/moe/dict_revised_${version}.xlsx > $(TMP_DIR)/tmp1.csv
	@csvcut -c 字詞名,注音一式 $(TMP_DIR)/tmp1.csv > $(TMP_DIR)/tmp2.csv
	@$(MISE_RUN) moe2csv.py -i $(TMP_DIR)/tmp2.csv -o $(LEXICON_DIR)/moe-revised.csv
	@-rm $(TMP_DIR)/tmp1.csv
	@-rm $(TMP_DIR)/tmp2.csv

# original dict_idioms_2020_20230629.xls came with incomplete fomular binding to foreign file
# must manually save as another copy to fix above question before using csvkit

idioms:
	@$(eval version = $(notdir $(wildcard $(RAWDATA_DIR)/moe/dict_idioms_*.xls)))
	@$(eval version = $(shell echo '${version}' | sed 's/dict_idioms_\(.*\)\.xls/\1/' ))
	@echo "idioms: ${version}"
	@sed -i '' -e 's/本詞庫來源版本：.*\n/本詞庫來源版本：${version}\n/g' $(LEXICON_DIR)/moe-idioms.csv.txt
	@in2csv $(RAWDATA_DIR)/moe/dict_idioms_${version}.xls > $(TMP_DIR)/tmp1.csv
	@csvcut -c 成語,注音 $(TMP_DIR)/tmp1.csv > $(TMP_DIR)/tmp2.csv
	@$(MISE_RUN) moe2csv.py -i $(TMP_DIR)/tmp2.csv -o $(LEXICON_DIR)/moe-idioms.csv
	@-rm $(TMP_DIR)/tmp1.csv
	@-rm $(TMP_DIR)/tmp2.csv

concised-xls:
	@$(eval version = $(notdir $(wildcard $(RAWDATA_DIR)/moe/dict_concised_*.xlsx)))
	@$(eval version = $(shell echo '${version}' | sed 's/dict_concised_\(.*\)\.xlsx/\1/' ))
	@echo "concised: ${version}"
	@sed -i '' -e 's/本詞庫來源版本：.*\n/本詞庫來源版本：${version}\n/g' $(LEXICON_DIR)/moe-concised.csv.txt
	@in2csv $(RAWDATA_DIR)/moe/dict_concised_${version}.xlsx > $(TMP_DIR)/tmp1.csv
	@csvcut -c 字詞名,注音一式 $(TMP_DIR)/tmp1.csv > $(TMP_DIR)/tmp2.csv
	@$(MISE_RUN) moe2csv.py -i $(TMP_DIR)/tmp2.csv -o $(LEXICON_DIR)/moe-concised.csv
	@-rm $(TMP_DIR)/tmp1.csv
	@-rm $(TMP_DIR)/tmp2.csv

concised-csv:
	@$(eval version = $(notdir $(wildcard $(RAWDATA_DIR)/moe/dict_concised_*.csv)))
	@$(eval version = $(shell echo '${version}' | sed 's/dict_concised_\(.*\)\.csv/\1/' ))
	@echo "concised: ${version}"
	@sed -i '' -e 's/本詞庫來源版本：.*\n/本詞庫來源版本：${version}\n/g' $(LEXICON_DIR)/moe-concised.csv.txt
	@cp $(RAWDATA_DIR)/moe/dict_concised_${version}.csv $(TMP_DIR)/tmp1.csv
# @csvcut --no-header-row --skip-lines 6 --columns a $(TMP_DIR)/tmp1.csv > $(TMP_DIR)/tmp2.csv
	@csvcut -c 字詞名,注音一式 $(TMP_DIR)/tmp1.csv > $(TMP_DIR)/tmp2.csv
	@$(MISE_RUN) moe2csv.py -i $(TMP_DIR)/tmp2.csv -o $(LEXICON_DIR)/moe-concised.csv
	@-rm $(TMP_DIR)/tmp1.csv
	@-rm $(TMP_DIR)/tmp2.csv


