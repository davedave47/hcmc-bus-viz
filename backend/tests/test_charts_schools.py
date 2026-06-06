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


def test_constellation_contract() -> None:
    body = client.get("/api/charts/schools/2.1").json()
    assert body["slug"] == "2.1"
    assert len(body["series"]) > 0
    assert {"slug", "student_boardings", "morning_peak_share", "nearby_stops"} <= body["series"][0].keys()


def test_treemap_contract() -> None:
    body = client.get("/api/charts/schools/2.2").json()
    assert len(body["series"]) > 0
    assert {"uni_slug", "route_no", "student_boardings"} <= body["series"][0].keys()


def test_weekly_default_and_filtered() -> None:
    body = client.get("/api/charts/schools/2.3").json()
    assert body["meta"]["applied"]["segment"] == "student"
    assert len(body["series"]) > 0
    assert {"dow", "hour", "boardings"} <= body["series"][0].keys()

    filtered = client.get(
        "/api/charts/schools/2.3", params={"segment": "all", "day_type": "weekend"}
    ).json()
    assert filtered["meta"]["applied"]["day_type"] == "weekend"
    assert "network pulses" in filtered["title"]


def test_proximity_contract() -> None:
    body = client.get("/api/charts/schools/2.4").json()
    assert len(body["series"]) >= 1
    assert "city_stops" in body["meta"]
    assert "catchment" in body["meta"]


def test_filters_endpoint() -> None:
    body = client.get("/api/filters").json()
    assert len(body["routes"]) > 0
    assert body["day_types"] == ["all", "weekday", "weekend"]
    assert body["date_range"]["min"] is not None
