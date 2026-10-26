# KEB Recursive Build + DMAIC System Makefile
# Orchestrates the complete lifecycle: ingest → parse → KPI → DMAIC → dashboard

.PHONY: help setup clean ingest parse kpi dmaic dashboard test all

# Default target
help:
	@echo "KEB Recursive Build + DMAIC System"
	@echo "=================================="
	@echo ""
	@echo "Available targets:"
	@echo "  setup     - Install dependencies and create directories"
	@echo "  clean     - Clean output and logs"
	@echo "  ingest    - Ingest MASTER.docx and create RTM"
	@echo "  parse     - Parse documents and extract requirements"
	@echo "  kpi       - Calculate KPIs (invCOP, helium losses, etc.)"
	@echo "  dmaic     - Run DMAIC loop with gate checks"
	@echo "  dashboard - Start Flask dashboard"
	@echo "  test      - Run all tests"
	@echo "  all       - Run complete pipeline"
	@echo ""
	@echo "Quick start: make setup && make all"

# Setup environment
setup:
	@echo "Setting up KEB environment..."
	python -m venv .venv
	.venv/bin/pip install -r requirements.txt
	mkdir -p output logs patches
	touch output/.keep logs/.keep
	@echo "Setup complete!"

# Clean outputs
clean:
	@echo "Cleaning outputs..."
	rm -rf output/* logs/* patches/*
	rm -f cd_success.flag
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	@echo "Clean complete!"

# Ingest MASTER.docx
ingest:
	@echo "Ingesting MASTER.docx..."
	python src/master_parser.py --input data/MASTER.docx --output output/rtm.json
	@echo "Ingestion complete!"

# Parse documents
parse:
	@echo "Parsing documents..."
	python src/requirement_parser.py --rtm output/rtm.json --output output/parsed_requirements.json
	@echo "Parsing complete!"

# Calculate KPIs
kpi:
	@echo "Calculating KPIs..."
	python src/kpi_calculator.py --requirements output/parsed_requirements.json --output output/kpis.json
	@echo "KPI calculation complete!"

# Run DMAIC loop
dmaic:
	@echo "Running DMAIC loop..."
	python src/dmaic_engine.py --kpis output/kpis.json --output output/dmaic_results.json
	@echo "DMAIC loop complete!"

# Start dashboard
dashboard:
	@echo "Starting Flask dashboard..."
	python dashboard_server.py

# Run tests
test:
	@echo "Running tests..."
	python -m pytest tests/ -v
	@echo "Tests complete!"

# Run complete pipeline
all: clean ingest parse kpi dmaic
	@echo "Complete KEB pipeline executed!"
	@echo "Results available in output/"
	@echo "Start dashboard with: make dashboard"

# Development helpers
dev-setup: setup
	.venv/bin/pip install pytest black flake8 mypy
	@echo "Development environment ready!"

lint:
	@echo "Running linters..."
	.venv/bin/black src/ tests/
	.venv/bin/flake8 src/ tests/
	.venv/bin/mypy src/

# CI/CD gate check
gate-check:
	@echo "Running CD gate checks..."
	python src/gate_checker.py --results output/dmaic_results.json
	@if [ -f cd_success.flag ]; then \
		echo "✅ CD Gate: PASSED"; \
	else \
		echo "❌ CD Gate: FAILED"; \
		exit 1; \
	fi