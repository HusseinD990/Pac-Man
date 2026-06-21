PYTHON      := python3
MAIN        := main.py
CON         := config.json

.DEFAULT_GOAL := run

install:
	uv sync

debug:
	uv run -m pdb $(MAIN) $(CON)

run:
	uv run $(MAIN) $(CON)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	uv run flake8 . --exclude=.venv
	uv run mypy . \
		--exclude '(^|/)\.venv(/|$$)' \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	mypy . --strict --exclude '(^|/)\.venv(/|$$)'