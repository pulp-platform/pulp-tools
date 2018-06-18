TARGET_INSTALL_DIR ?= $(CURDIR)/install
INSTALL_DIR ?= $(CURDIR)/install
BUILD_DIR   ?= $(CURDIR)/build

all: header build

export PYTHONPATH:=$(CURDIR)/bin:$(PYTHONPATH)

define declareInstallFile

$(INSTALL_DIR)/$(1): $(1)
	install -D $(1) $$@

INSTALL_HEADERS += $(INSTALL_DIR)/$(1)

endef


INSTALL_FILES += $(shell find python -name *.py)
INSTALL_FILES += bin/plpconf
INSTALL_FILES += bin/plpbuild
INSTALL_FILES += bin/plpflags
INSTALL_FILES += bin/plpinfo
INSTALL_FILES += bin/plptest

$(INSTALL_DIR)/bin/plptest_checker: $(BUILD_DIR)/plptest_checker
	install -D $< $@

$(BUILD_DIR)/plptest_checker: src/plptest_checker.c
	mkdir -p $(BUILD_DIR)
	gcc -O3 -g src/plptest_checker.c -o $(BUILD_DIR)/plptest_checker

$(foreach file, $(INSTALL_FILES), $(eval $(call declareInstallFile,$(file))))

# This file is a dummy one that is updated as soon as one of the tools file is updated
# This is used to trigger automatic application recompilation
$(TARGET_INSTALL_DIR)/rules/tools.mk: $(INSTALL_HEADERS)
	@mkdir -p `dirname $@`
	touch $@

header: $(TARGET_INSTALL_DIR)/rules/tools.mk

build: $(INSTALL_DIR)/bin/plptest_checker
