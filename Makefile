all:
	ifeq (, $(shell which pip))
		ifeq (, $(shell which pip3))
			$(error "No pip or pip3 present on system.")
		else:
			# pip3
			PYPIP=pip3
	else:
		PYPIP=pip

	$(PYPIP) -r python/requirements.txt
