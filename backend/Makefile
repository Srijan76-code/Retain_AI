.PHONY: dev fastapi inngest install

# Default shell
SHELL := /bin/bash

# Configuration
PYTHON_VENV := .venv
PYTHON_BIN := $(PYTHON_VENV)/bin/python
UVICORN_BIN := $(PYTHON_VENV)/bin/uvicorn
APP_MODULE := app.main:app
PORT := 8000
INNGEST_URL := http://127.0.0.1:$(PORT)/api/inngest

install:
	python3 -m venv $(PYTHON_VENV)
	$(PYTHON_VENV)/bin/pip install -r requirements.txt

fastapi:
	$(UVICORN_BIN) $(APP_MODULE) --reload --port $(PORT)

inngest:
	npx inngest-cli@latest dev -u $(INNGEST_URL)

dev:
	@echo "Starting FastAPI and Inngest Dev Server..."
	@npx concurrently -n "FastAPI,Inngest" -c "cyan,magenta" \
		"$(UVICORN_BIN) $(APP_MODULE) --reload --port $(PORT)" \
		"npx inngest-cli@latest dev -u $(INNGEST_URL)"
