from fastapi.testclient import TestClient

from busanalytics_api.main import app


def test_healthz_ok() -> None:
    response = TestClient(app).get("/api/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "warehouse_ready" in body
