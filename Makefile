PYTHON      := python3
PIP         := pip
MAIN        := pac-man.py
CON         := config.json

.DEFAULT_GOAL := run

install:
	$(PIP) install -r requirements.txt

debug:
	$(PYTHON) -m pdb $(MAIN) $(CON)

run:
	$(PYTHON) $(MAIN) $(CON)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	python3 -m flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	mypy . --strict