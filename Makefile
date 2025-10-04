.PHONY: all setup run benchmark report clean

MODE ?= baseline
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

all: setup run benchmark report

setup:
	@echo "📦 Creating virtual environment and installing dependencies..."
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	@echo "🐳 Building containers..."
	docker compose build
	@echo "🚀 Starting containers..."
	docker compose up -d

benchmark:
	@echo "⏱ Running benchmark in mode: $(MODE)"
	sudo bash ./wrk_test.sh $(MODE)

report:
	@echo "📄 Generating benchmark report..."
	$(PYTHON) ./wrk_analysis.py

clean:
	@echo "🧹 Cleaning up..."
	docker compose down
	rm -rf benchmark_report benchmark_charts benchmark_log $(VENV)
