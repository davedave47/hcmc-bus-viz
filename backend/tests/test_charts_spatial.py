from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from busanalytics_api.config import settings
from busanalytics_api.main import app

pytestmark = pytest.mark.skipif(
    not Path(settings.db_path).exists(),
    reason="db/bus.duckdb not present (CI / fresh checkout)",
)

client = TestClient(app)


def test_density_contract() -> None:
    body = client.get("/api/charts/spatial/3.1").json()
    assert body["slug"] == "3.1"
    assert len(body["series"]) > 0
    assert {"lat", "lng", "boardings"} <= body["series"][0].keys()
    assert 0 < body["meta"]["top_share"] <= 100


def test_metro_sankey_contract() -> None:
    body = client.get("/api/charts/spatial/3.2").json()
    assert len(body["series"]) > 0  # links
    assert {"source", "target", "value"} <= body["series"][0].keys()
    assert len(body["meta"]["nodes"]) > 14  # base + 14 metro + feeder routes
    assert body["meta"]["feeder_count"] > 0


def test_isochrone_contract() -> None:
    body = client.get("/api/charts/spatial/3.4").json()
    assert body["meta"]["origin"] is not None
    bands = {p["band"] for p in body["series"]}
    assert 0 in bands and 1 in bands  # origin + first ring
    assert body["meta"]["band2_n"] >= 0
