.PHONY: lint test

lint:
	flake8 src tests

test: lint
	pytest --cov=src --cov-report=term-missing
