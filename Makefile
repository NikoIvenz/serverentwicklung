.PHONY: help install db-up db-down run test lint format typecheck check clean

COMPOSE := docker compose -f postgres-setup/compose.yml

.DEFAULT_GOAL := help

help: ## Show this help
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

install: ## Install all dependencies
	uv sync

db-up: ## Start the PostgreSQL container
	$(COMPOSE) up -d

db-down: ## Stop the PostgreSQL container
	$(COMPOSE) down

run: ## Start the server (https://127.0.0.1:8000/docs)
	uv run auto

test: ## Run the tests (needs the database)
	uv run pytest

lint: ## Run ruff checks
	uv run ruff check

format: ## Fix lint issues and format the code
	uv run ruff check --fix
	uv run ruff format

typecheck: ## Run pyright
	uv run pyright

check: lint typecheck test ## Run lint, type check and tests

clean: ## Remove generated reports and caches
	rm -rf report.html assets htmlcov .coverage .pytest_cache .ruff_cache
