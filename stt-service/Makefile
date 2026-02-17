.PHONY: lint format check typecheck

lint: format check typecheck

format:
	uv run ruff format .

check:
	uv run ruff check . --fix

typecheck:
	uv run mypy .