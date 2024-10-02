# Makefile for managing a Django app with Poetry

# Variables
POETRY := poetry
PYTHON := $(POETRY) run python
MANAGE := $(PYTHON) manage.py

# Default target
.PHONY: help
help:
	@echo "Usage:"
	@echo "  make install       Install dependencies"
	@echo "  make migrate       Apply database migrations"
	@echo "  make run           Run the Django development server"
	@echo "  make shell         Open a Django shell"
	@echo "  make test          Run tests"
	@echo "  make lint          Run linters"

# Install dependencies
.PHONY: install
install:
	$(POETRY) install

# Apply database migrations
.PHONY: migrate
migrate:
	$(MANAGE) migrate

# Run the Django development server
.PHONY: run
run:
	$(MANAGE) runserver

# Open a Django shell
.PHONY: shell
shell:
	$(MANAGE) shell

# Run tests
.PHONY: test
test:
	$(POETRY) run pytest

# Deploy the app
.PHONY: deploy
deploy:
	$(MANAGE) collectstatic --noinput
	$(MANAGE) migrate
	$(MANAGE) runserver
