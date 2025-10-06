.PHONY: all setup benchmark report

MODE ?= short
VENV := .venv
PIP := $(VENV)/bin/pip

all: setup benchmark report

setup:
	@echo "📦 Creating virtual environment and installing dependencies..."
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

	@echo "🗂 Creating required benchmark directories..."
	mkdir -p benchmark_log benchmark_charts benchmark_report
	touch wrk_test.sh wrk_analysis.py
	chmod +x wrk_test.sh

benchmark:
	@echo "🐳 Building and starting containers..."
	docker compose up -d --build --force-recreate
	docker exec wrk bash -c "bash ./wrk_test.sh $(MODE)"

report:
	@echo "📄 Generating benchmark report..."
	docker exec wrk python3 /app/wrk_analysis.py
