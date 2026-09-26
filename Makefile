.PHONY: lint test

lint:
	flake8 src tests --select=E9,F63,F7,F82

test: lint
	pytest --cov=src --cov-report=term-missing
