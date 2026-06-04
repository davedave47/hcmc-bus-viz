# HCMC Bus Analytics — how to run the dashboard
#
# Quick start (you only need these two):
#   make install     # one time: install the Python packages
#   make run         # start the dashboard, then open http://localhost:8000
#
# Other targets:
#   make stop        # stop the dashboard (frees the port)
#   make build       # rebuild the warehouse db/bus.duckdb from raw inputs
#   make help        # list targets

PORT := 8000
PY   := .venv/bin/python
PIP  := .venv/bin/pip

.PHONY: help install build run serve stop

help:
	@echo "make install  - install the Python packages into .venv"
	@echo "make run      - start the dashboard at http://localhost:$(PORT)"
	@echo "make stop     - stop the dashboard"
	@echo "make build    - rebuild the warehouse (db/bus.duckdb)"

# create the virtualenv if it does not exist yet
.venv:
	python3 -m venv .venv

install: .venv
	$(PIP) install -U pip
	$(PIP) install -r demo/requirements.txt

# (re)build the analytical warehouse from the raw inputs
build:
	$(PY) -m demo.warehouse.build

# start the web app — leave this running, open the URL in a browser
run:
	@echo ""
	@echo "  Dashboard  ->  http://localhost:$(PORT)"
	@echo "  Press Ctrl-C in this terminal to stop."
	@echo ""
	$(PY) -m uvicorn demo.main:app --reload --port $(PORT)

serve: run

# stop a running dashboard (free the port)
stop:
	-@fuser -k $(PORT)/tcp 2>/dev/null || true
	@echo "dashboard stopped"
