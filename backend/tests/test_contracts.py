"""Contract tests — every endpoint runs against the synthetic fixture warehouse.

These run in CI (no real data). They assert the endpoint works end-to-end (SQL is
valid against the expected schema, the service computes, the ChartResponse shape
validates) — guarding the backend<->warehouse seam. Exact production numbers live
in the data-gated integration tests.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

CHARTS = [
    ("schools", "2.1"),
    ("schools", "2.2"),
    ("schools", "2.3"),
    ("schools", "2.4"),
    ("spatial", "3.1"),
    ("spatial", "3.2"),
    ("spatial", "3.4"),
    ("health", "5.1"),
    ("health", "5.2"),
]


@pytest.mark.parametrize(("theme", "slug"), CHARTS)
def test_chart_contract(client: TestClient, theme: str, slug: str) -> None:
    res = client.get(f"/api/charts/{theme}/{slug}")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["theme"] == theme
    assert body["slug"] == slug
    assert isinstance(body["title"], str) and body["title"]
    assert isinstance(body["series"], list)
    assert isinstance(body["encoding"], dict)
    assert isinstance(body["meta"], dict)


def test_kpis_contract(client: TestClient) -> None:
    body = client.get("/api/kpis").json()
    assert {"boardings", "routes_n", "stops_n", "student_share"} <= body.keys()


def test_filters_contract(client: TestClient) -> None:
    body = client.get("/api/filters").json()
    assert isinstance(body["routes"], list)
    assert body["day_types"] == ["all", "weekday", "weekend"]
    assert "date_range" in body


def test_weekly_filter_applies(client: TestClient) -> None:
    body = client.get("/api/charts/schools/2.3", params={"segment": "all", "day_type": "weekend"}).json()
    assert body["meta"]["applied"]["segment"] == "all"
    assert body["meta"]["applied"]["day_type"] == "weekend"


def test_unknown_theme_422(client: TestClient) -> None:
    assert client.get("/api/charts/nope/1.1").status_code == 422


def test_unknown_slug_404(client: TestClient) -> None:
    assert client.get("/api/charts/health/9.9").status_code == 404
