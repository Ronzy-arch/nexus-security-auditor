.PHONY: install test lint format run clean version

install:
	pip install -r requirements.txt

test:
	pytest

lint:
	ruff check .

format:
	black .

run:
	python3 main.py

version:
	python3 main.py version

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
