SHELL := /bin/bash
.SHELLFLAGS := -euo pipefail -c
.DEFAULT_GOAL := help

# Colors for pretty printing
BLUE := \033[34m
NC := \033[0m  # No Color
INFO := @printf "$(BLUE)%s$(NC)\n"

# Command line arguments
ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))

.PHONY: all clean setup test lint format check help run install-global uninstall-global

setup:  ## Install dependencies using uv
	$(INFO) "Installing dependencies..."
	@command -v uv >/dev/null 2>&1 || \
		{ echo "uv is not installed. Installing..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; }
	@uv venv
	@uv pip install -e ".[dev]"

install-global: clean  ## Install h-cli globally using pipx
	$(INFO) "Installing h-cli globally..."
	@pipx install . --force --python python3

uninstall-global:  ## Uninstall h-cli globally
	$(INFO) "Uninstalling h-cli globally..."
	@pipx uninstall h-cli

test: ## Run tests with coverage
	$(INFO) "Running tests..."
	@uv run pytest tests/ \
		--cov=h \
		--cov-report=term-missing \
		--cov-report=html \
		-v

lint: ## Run linting (black, isort, mypy)
	$(INFO) "Running linters..."
	@uv run black h/ tests/
	@uv run isort h/ tests/
	@PYTHONPATH=. uv run mypy h/ tests/

format: ## Format code using black and isort
	$(INFO) "Formatting code..."
	@uv run black h/ tests/
	@uv run isort h/ tests/

run: ## Run the CLI tool (use: make run -- --help)
	$(INFO) "Running h-cli..."
	@uv run h $(ARGS)

check: lint test ## Run all checks (linting and tests)

clean: ## Clean up generated files and virtual environment
	$(INFO) "Cleaning up..."
	@rm -rf .venv/
	@rm -rf .pytest_cache
	@rm -rf .coverage
	@rm -rf htmlcov
	@rm -rf .mypy_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type f -name ".coverage" -delete
	@find . -type f -name ".coverage.*" -delete

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(BLUE)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Pass through arguments
%:
	@:
