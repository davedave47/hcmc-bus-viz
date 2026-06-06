from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from busanalytics_api.config import settings
from busanalytics_api.main import app

pytestmark = pytest.mark.skipif(
    not Path(settings.db_path).exists(),
    reason="db/bus.duckdb not present (CI / fresh checkout)",
)


def test_kpis_returns_warehouse_numbers() -> None:
    response = TestClient(app).get("/api/kpis")
    assert response.status_code == 200
    body = response.json()
    assert body["boardings"] == 17883623
    assert body["routes_n"] > 0
    assert body["stops_n"] > 0
