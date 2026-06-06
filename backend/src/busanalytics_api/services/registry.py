"""Chart registry — (theme, slug) → service.

Open/closed: add a chart by registering its service here; the router never changes.
Each service takes the injected `Warehouse` and returns a `ChartResponse`.
"""
from __future__ import annotations

from collections.abc import Callable

from ..db import Warehouse
from ..domain import ChartKey, Theme
from ..schemas import ChartResponse
from .charts import health

ChartService = Callable[[Warehouse], ChartResponse]

CHART_SERVICES: dict[ChartKey, ChartService] = {
    (Theme.health, "5.1"): health.pulse,
    (Theme.health, "5.2"): health.qos,
}
