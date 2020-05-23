.PHONY: all
all: update-snapshots

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
