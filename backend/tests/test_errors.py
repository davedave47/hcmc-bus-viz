from typing import Any

from fastapi.testclient import TestClient

from busanalytics_api.api.deps import get_warehouse
from busanalytics_api.main import app


def test_missing_warehouse_returns_structured_503() -> None:
    def boom() -> Any:
        raise FileNotFoundError("no warehouse here")

    app.dependency_overrides[get_warehouse] = boom
    try:
        res = TestClient(app, raise_server_exceptions=False).get("/api/kpis")
        assert res.status_code == 503
        assert res.json()["error"] == "warehouse_unavailable"
    finally:
        app.dependency_overrides.clear()


class _BoomWarehouse:
    def query(self, sql: str, params: Any = None) -> list[dict[str, Any]]:
        raise RuntimeError("query failed")

    def query_one(self, sql: str, params: Any = None) -> dict[str, Any] | None:
        raise RuntimeError("query failed")

    def close(self) -> None:  # pragma: no cover
        pass


def test_query_failure_returns_structured_500() -> None:
    app.dependency_overrides[get_warehouse] = lambda: _BoomWarehouse()
    try:
        # unique query param -> cache miss -> the service actually runs and raises
        res = TestClient(app, raise_server_exceptions=False).get("/api/charts/health/5.1?_cb=err")
        assert res.status_code == 500
        assert res.json()["error"] == "internal_error"
    finally:
        app.dependency_overrides.clear()
