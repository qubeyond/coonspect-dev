#!/bin/bash
set -e

cd "$(dirname "$0")/.."

echo "Current directory: $(pwd)"

echo "Running Ruff formatter..."
uv run ruff format .

echo "Running Ruff linter..."
uv run ruff check . --fix

echo "Running Mypy type check..."
uv run mypy .

echo "All checks passed!"