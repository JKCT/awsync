.PHONY: init
init:
	poetry install --sync

.PHONY: run
run:
	poetry run python -B awsync

.PHONY: format
format:
	poetry run black awsync tests

.PHONY: lint
lint:
	./version_check.sh # Checks branch version is updated from main
	poetry check # Checks lockfile is up to date
	poetry run black --check awsync tests
	poetry run mypy awsync tests

.PHONY: test
test:
	poetry run python -B -m pytest

.PHONY: docs
docs:
	./docs.sh

.PHONY: release
release:
	./release.sh $(TOKEN)

.PHONY: publish
publish:
	poetry publish --build

.PHONY: pr
pr: format lint test
