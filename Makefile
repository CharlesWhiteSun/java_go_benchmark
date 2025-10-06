.PHONY: all setup benchmark report

MODE ?= baseline
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

all: setup benchmark report

setup:
	@echo "📦 Creating virtual environment and installing dependencies..."
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

benchmark:
	@echo "🐳 Building and starting containers..."
	docker compose up -d --build --force-recreate
	docker exec wrk bash -c "bash ./wrk_test.sh $(MODE)"

report:
	@echo "📄 Generating benchmark report..."
	$(PYTHON) ./wrk_analysis.py
