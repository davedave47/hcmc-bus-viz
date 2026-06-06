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


def test_pulse_contract() -> None:
    response = client.get("/api/charts/health/5.1")
    assert response.status_code == 200
    body = response.json()
    assert body["theme"] == "health"
    assert body["slug"] == "5.1"
    assert body["title"]  # a non-empty computed action title
    assert len(body["series"]) > 0
    assert {"day", "boardings"} <= body["series"][0].keys()
    assert body["meta"]["tet_start"] is not None


def test_qos_contract() -> None:
    response = client.get("/api/charts/health/5.2")
    assert response.status_code == 200
    body = response.json()
    assert body["slug"] == "5.2"
    assert len(body["series"]) > 0
    assert {"route_no", "qos1", "qos2", "qos3"} <= body["series"][0].keys()


def test_unknown_chart_404() -> None:
    assert client.get("/api/charts/health/9.9").status_code == 404
