.DEFAULT_GOAL := help
.PHONY: help install lint test check score badge build dist-check clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install: ## Install the package with dev extras (editable)
	pip install -e '.[dev]'

lint: ## Run ruff
	ruff check src tests

test: ## Run the test suite
	pytest -q

check: lint test ## Run the full CI gate (lint + test)

score: ## Score the bundled example skills
	agentskills-ci score examples/skills

badge: ## Print a quality badge for the good example skill
	agentskills-ci badge examples/skills/good-skill

build: ## Build sdist + wheel into dist/
	python -m build

dist-check: build ## Build then validate distributions with twine
	python -m twine check dist/*

clean: ## Remove build/test artifacts
	rm -rf dist build *.egg-info .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
