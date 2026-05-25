.PHONY: tangle check test install dev clean help

PY ?= python3

help:
	@echo "sakshi — Makefile"
	@echo ""
	@echo "  make tangle    Tangle codev/*.org -> src/sakshi/*.py and test/*.py"
	@echo "  make check     Exit non-zero if any tangled file is out-of-sync"
	@echo "  make install   pip install -e ."
	@echo "  make dev       pip install -e '.[test,dev]'"
	@echo "  make test      pytest"
	@echo "  make clean     Remove tangled outputs and __pycache__"

tangle:
	$(PY) develop/tangle.py

check:
	$(PY) develop/tangle.py --check

install:
	pip install -e .

dev:
	pip install -e '.[test,dev]'

test: tangle
	pytest

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
