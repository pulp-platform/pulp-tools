
define declareInstallFile

$(PULP_SDK_WS_INSTALL)/$(1): $(1)
	install -D $(1) $$@

INSTALL_HEADERS += $(PULP_SDK_WS_INSTALL)/$(1)

endef

define declareEnvInstallFile

$(PULP_SDK_HOME)/$(1): $(1)
	install -D $(1) $$@

INSTALL_HEADERS += $(PULP_SDK_HOME)/$(1)

endef


INSTALL_FILES += $(shell find bin -name *.py)
INSTALL_FILES += bin/plpbuild
INSTALL_FILES += bin/plpflags
INSTALL_FILES += bin/plpinfo
INSTALL_FILES += bin/plptest
INSTALL_FILES += $(PULP_SDK_INSTALL)/bin/plptest_checker
INSTALL_FILES += $(shell find configs -name *.json)

$(PULP_SDK_INSTALL)/bin/plptest_checker: src/plptest_checker.c
	mkdir -p $(PULP_SDK_INSTALL)/bin/
	gcc -O3 -g src/plptest_checker.c -o $(PULP_SDK_INSTALL)/bin/plptest_checker

$(foreach file, $(INSTALL_FILES), $(eval $(call declareInstallFile,$(file))))

# This file is a dummy one that is updated as soon as one of the tools file is updated
# This is used to trigger automatic application recompilation
$(PULP_SDK_INSTALL)/rules/tools.mk: $(INSTALL_HEADERS)
	@mkdir -p `dirname $@`
	touch $@

header: $(PULP_SDK_INSTALL)/rules/tools.mk

pulp.gen:
	./generators/pulp_soc_gen > configs/chips/pulp/soc.json

gen: pulp.gen