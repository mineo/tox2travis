.PHONY: all
all: self

.PHONY: sanity
sanity:
	# Check if the working directory is clean, that is, there are no unstaged
	# changes to already tracked files.
	git diff-index --quiet HEAD

.PHONY: update-snapshots
update-snapshots: sanity
	rm -rf snapshots/*
	pytest --snapshot-update
	git add snapshots
	git commit -m "Update test snapshots"

.PHONY: .github/workflows/tox.yml
.github/workflows/tox.yml:
	tox2travis --fallback-python=python3.7 --output=actions

.PHONY: .travis.yml
.travis.yml:
	tox2travis --fallback-python=python3.7

.PHONY: dogfood
dogfood: self

.PHONY: self
self: .travis.yml .github/workflows/tox.yml
