"""A small synthetic warehouse so the API contract is tested in CI (no real data).

`_build_fixture_warehouse` creates every table/column the repositories read, with a
few representative rows — enough that all SQL runs and the endpoints return valid
ChartResponse shapes. This guards the backend<->warehouse schema seam; exact
production numbers (e.g. 17,883,623) stay in the data-gated integration tests.
"""
from __future__ import annotations

from collections.abc import Iterator

import duckdb
import pytest
from fastapi.testclient import TestClient

from busanalytics_api.api import deps
from busanalytics_api.api.routers import charts as charts_router
from busanalytics_api.db import DuckDBWarehouse
from busanalytics_api.main import app


def _build_fixture_warehouse(path: str) -> None:
    con = duckdb.connect(path)
    con.execute("""
        CREATE TABLE dim_date(day DATE, is_tet_2026 BOOLEAN,
                              is_tet_2026_trough BOOLEAN, is_pre_tet_baseline BOOLEAN);
        INSERT INTO dim_date VALUES
          (DATE '2026-01-10', false, false, true),
          (DATE '2026-02-14', true,  false, false),
          (DATE '2026-02-16', true,  true,  false),
          (DATE '2026-02-22', true,  false, false),
          (DATE '2026-03-01', false, false, false);

        CREATE TABLE dim_school(school_slug VARCHAR, display VARCHAR, stop_id BIGINT,
                                lat DOUBLE, lng DOUBLE, verified BOOLEAN);
        INSERT INTO dim_school VALUES
          ('HCMUT', 'Bách Khoa', 506, 10.7726, 106.6577, true),
          ('USSH',  'KHXH',      1096, 10.7858, 106.7027, true);

        CREATE TABLE dim_stop(stop_id BIGINT, name VARCHAR, lat DOUBLE, lng DOUBLE,
                              in_bbox BOOLEAN, routes_csv VARCHAR);
        INSERT INTO dim_stop VALUES
          (35,  'Origin',        10.77,   106.70,   true, '01,02'),
          (506, 'Near HCMUT',    10.7726, 106.6577, true, '01'),
          (1096,'Near USSH',     10.7858, 106.7027, true, '02'),
          (900, 'Near Metro BTH',10.7721, 106.6987, true, '01,03'),
          (901, 'Shares 01',     10.78,   106.70,   true, '01');

        CREATE TABLE agg_stop_total(stop_id BIGINT, name VARCHAR, lat DOUBLE,
                                    lng DOUBLE, boardings BIGINT);
        INSERT INTO agg_stop_total VALUES
          (35, 'Origin', 10.77, 106.70, 5000),
          (506,'Near HCMUT', 10.7726, 106.6577, 3000),
          (900,'Near Metro BTH', 10.7721, 106.6987, 4000),
          (901,'Shares 01', 10.78, 106.70, 1000);

        CREATE TABLE agg_network_day(day DATE, fare_class VARCHAR, boardings BIGINT);
        INSERT INTO agg_network_day VALUES
          (DATE '2026-01-10','student',1000),(DATE '2026-01-10','cash',1500),
          (DATE '2026-02-16','student',200), (DATE '2026-02-16','cash',300),
          (DATE '2026-03-01','student',900), (DATE '2026-03-01','cash',1400);

        CREATE TABLE agg_route_hour(route_no VARCHAR, dow INTEGER, hour INTEGER,
                                    fare_class VARCHAR, boardings BIGINT);
        INSERT INTO agg_route_hour VALUES
          ('01',1,7,'student',500),('01',1,17,'cash',500),('01',2,8,'student',400),
          ('02',1,7,'student',300),('02',3,18,'cash',200);

        CREATE TABLE agg_school_route(uni_slug VARCHAR, route_no VARCHAR,
                                      fare_class VARCHAR, dow INTEGER, hour INTEGER,
                                      boardings BIGINT);
        INSERT INTO agg_school_route VALUES
          ('HCMUT','01','student',1,7,400),('HCMUT','02','student',1,8,120),
          ('USSH','01','student',1,7,300);

        CREATE TABLE agg_hub_kpis(boardings BIGINT, revenue DOUBLE, student_share DOUBLE,
                                  routes_n INTEGER, stops_n INTEGER, metro_feeders INTEGER);
        INSERT INTO agg_hub_kpis VALUES (5300, 21000000, 36.0, 2, 5, 1);

        CREATE TABLE fact_boardings(day DATE, hour INTEGER, route_no VARCHAR, fare_class VARCHAR);
        INSERT INTO fact_boardings VALUES
          (DATE '2026-01-10',7,'01','student'),(DATE '2026-01-10',8,'01','student'),
          (DATE '2026-03-01',17,'02','cash'),  (DATE '2026-03-01',7,'01','free');
    """)
    con.close()


@pytest.fixture(scope="session")
def fixture_db(tmp_path_factory: pytest.TempPathFactory) -> str:
    path = str(tmp_path_factory.mktemp("warehouse") / "fixture.duckdb")
    _build_fixture_warehouse(path)
    return path


@pytest.fixture
def client(fixture_db: str) -> Iterator[TestClient]:
    """A TestClient whose warehouse is the synthetic fixture (no real data)."""
    warehouse = DuckDBWarehouse(fixture_db)
    app.dependency_overrides[deps.get_warehouse] = lambda: warehouse
    charts_router.clear_caches()
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        charts_router.clear_caches()
        warehouse.close()
