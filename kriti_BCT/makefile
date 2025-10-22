# Makefile for Saturnin & PRESENT S-box BCT generator

PYTHON := python3
SCRIPT := saturnin_bct.py

.PHONY: all run lint clean help

all: run

## Run the BCT generator
run:
	@echo "🚀 Running Boomerang Connectivity Table generator..."
	@$(PYTHON) $(SCRIPT)

## Check code style (optional)
lint:
	@echo "🔍 Checking code style with flake8..."
	@flake8 $(SCRIPT) || echo "⚠️  Install flake8 with: pip install flake8"

## Remove cache and temporary files
clean:
	@echo "🧹 Cleaning up..."
	@rm -rf __pycache__ .pytest_cache *.pyc

## Display available commands
help:
	@echo ""
	@echo "Available Make targets:"
	@echo "  make run     – Run the BCT generator"
	@echo "  make lint    – Run flake8 linter (if installed)"
	@echo "  make clean   – Remove cache files"
	@echo "  make help    – Show this help message"
	@echo ""
