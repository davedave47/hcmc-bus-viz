# HCMC Bus Analytics — dev tasks. Run `make help` for the list.
#
# Phase-2 stack lives in three packages:
#   backend/  (uv)   data API     ->  http://localhost:8000
#   frontend/ (pnpm) web app      ->  http://localhost:5173
#   pipeline/ (uv)   warehouse    (scaffold; build pending)

PORT_API := 8000
PORT_WEB := 5173
PY       := .venv/bin/python   # legacy demo / warehouse builder

.PHONY: help backend frontend up down test lint warehouse demo install-demo stop

help:
	@echo "Phase-2 stack:"
	@echo "  make backend    - data API (uvicorn, reload) on :$(PORT_API)"
	@echo "  make frontend   - web app (vite) on :$(PORT_WEB)"
	@echo "  make up / down  - run / stop backend + frontend in Docker"
	@echo "  make test       - backend + frontend + pipeline tests"
	@echo "  make lint       - ruff + mypy (backend), eslint (frontend)"
	@echo "Data + legacy:"
	@echo "  make warehouse  - (re)build db/bus.duckdb from raw inputs"
	@echo "  make demo       - run the legacy Phase-1 prototype on :$(PORT_API)"
	@echo "  make stop       - free ports $(PORT_API) and $(PORT_WEB)"

# ---- Phase-2 stack ----
backend:
	cd backend && uv run uvicorn busanalytics_api.main:app --reload --port $(PORT_API)

frontend:
	cd frontend && pnpm dev

up:
	docker compose up --build

down:
	docker compose down

test:
	cd backend  && uv run pytest -q
	cd frontend && pnpm test
	cd pipeline && uv run pytest -q

lint:
	cd backend  && uv run ruff check . && uv run mypy src
	cd frontend && pnpm lint

# ---- data warehouse (db/bus.duckdb is read by the backend until the pipeline lands) ----
.venv:
	python3 -m venv .venv
	$(PY) -m pip install -U pip
	$(PY) -m pip install -r demo/requirements.txt

install-demo: .venv

warehouse: .venv
	$(PY) -m demo.warehouse.build

# ---- legacy Phase-1 prototype ----
demo: .venv
	@echo "  legacy prototype -> http://localhost:$(PORT_API)  (Ctrl-C to stop)"
	$(PY) -m uvicorn demo.main:app --reload --port $(PORT_API)

stop:
	-@fuser -k $(PORT_API)/tcp 2>/dev/null || true
	-@fuser -k $(PORT_WEB)/tcp 2>/dev/null || true
	@echo "ports $(PORT_API) and $(PORT_WEB) freed"
