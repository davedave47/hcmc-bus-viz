"""FastAPI entrypoint for the HCMC Bus Analytics demo surface.

Run with:
    uvicorn demo.main:app --reload --port 8000
"""
from __future__ import annotations

import datetime
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import db
from .routers import api, health, hub, schools, spatial, story_tet

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")

_HERE = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(_HERE / "templates"))


def _afc_window() -> str:
    """Data-window pill text, read from the warehouse so it can never drift
    from the AFC dates actually loaded (e.g. 'Jan 1 – Mar 31, 2026')."""
    row = db.query_one("SELECT MIN(day) AS lo, MAX(day) AS hi FROM agg_network_day")
    if not row or not row["lo"]:
        return ""
    lo = row["lo"] if isinstance(row["lo"], datetime.date) else datetime.date.fromisoformat(str(row["lo"]))
    hi = row["hi"] if isinstance(row["hi"], datetime.date) else datetime.date.fromisoformat(str(row["hi"]))
    return f"{lo.strftime('%b %-d')} – {hi.strftime('%b %-d, %Y')}"


TEMPLATES.env.globals["afc_window"] = ""


@asynccontextmanager
async def lifespan(_app: FastAPI):
    db.get_conn()
    TEMPLATES.env.globals["afc_window"] = _afc_window()
    yield
    db.close()


app = FastAPI(title="HCMC Bus Analytics", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=str(_HERE / "static")), name="static")
app.state.templates = TEMPLATES

app.include_router(api.router)
app.include_router(hub.router)
app.include_router(schools.router)
app.include_router(spatial.router)
app.include_router(health.router)
app.include_router(story_tet.router)
