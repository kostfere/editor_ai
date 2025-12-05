.PHONY: help install run lint format typecheck check clean

# Default target
help:
	@echo "EditorAI - Available commands:"
	@echo ""
	@echo "  make install    - Install dependencies with Poetry"
	@echo "  make run        - Start the Streamlit app"
	@echo "  make lint       - Run ruff linter"
	@echo "  make format     - Format code with ruff"
	@echo "  make typecheck  - Run pyright type checker"
	@echo "  make check      - Run all checks (lint + typecheck)"
	@echo "  make fix        - Auto-fix linting issues"
	@echo "  make clean      - Remove cache files"
	@echo ""

# Install dependencies
install:
	poetry install

# Run the Streamlit app
run:
	poetry run streamlit run app.py

# Run ruff linter
lint:
	poetry run ruff check .

# Format code with ruff
format:
	poetry run ruff format .

# Run pyright type checker
typecheck:
	poetry run pyright

# Run all checks
check: lint typecheck
	@echo "✅ All checks passed!"

# Auto-fix linting issues
fix:
	poetry run ruff check . --fix
	poetry run ruff format .

# Clean cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pyright" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "🧹 Cleaned cache files"

