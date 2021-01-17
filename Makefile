#!/usr/bin/env make

prog1=pip3
prog2=pip

ifeq (, $(shell which $(prog1)))
	$(info No $(prog1), continuing to resolve $(prog2))
	ifeq (, $(shell which $(prog2)))
		$(error Neither $(prog1) or $(prog2) was detected)
	else
		#$(info Found $(prog2))
		exe=$(prog2)
	endif
else
	#$(info Found $(prog1))
	exe=$(prog1)
endif

$(info proceeding with $(exe))


.phony: execute

execute:
	$(info resolving dependencies)
	$(exe) install -r python/requirements.txt