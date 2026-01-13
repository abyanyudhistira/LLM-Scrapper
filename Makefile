.PHONY: install test run clean help

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run tests"
	@echo "  make run        - Run example"
	@echo "  make test-match - Run interactive test"
	@echo "  make clean      - Clean cache files"

install:
	python -m pip install -r requirements.txt

test:
	python -m pytest tests/ -v

run:
	python -m app.main

test-match:
	python test_matching.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
