.PHONY: init
init:
	poetry install --sync

.PHONY: run
run:
	poetry run python -B awsync

.PHONY: lint
lint:
	poetry check
	poetry run black --check awsync tests
	poetry run mypy awsync tests

.PHONY: format
format:
	poetry run black awsync tests

.PHONY: test
test:
	poetry run python -B -m pytest

.PHONY: release
release:
	echo "disabled until implementation is complete"
	#./automatic_release.sh

.PHONY: publish
publish:
	./version_check.sh $(ARGS)
	poetry publish --build

.PHONY: pr
pr: format lint test
