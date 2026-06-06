"""Chart registry — (theme, slug) → service.

Open/closed: add a chart by registering its service here; the router never changes.
Each service takes the injected `Warehouse` and returns a `ChartResponse`.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping

from ..db import Warehouse
from ..domain import ChartKey, Theme
from ..schemas import ChartResponse
from .charts import health, schools

# Every service takes the injected warehouse + the request filters (query params).
ChartService = Callable[[Warehouse, Mapping[str, str]], ChartResponse]

CHART_SERVICES: dict[ChartKey, ChartService] = {
    (Theme.schools, "2.1"): schools.constellation,
    (Theme.schools, "2.2"): schools.treemap,
    (Theme.schools, "2.3"): schools.weekly_heatmap,
    (Theme.schools, "2.4"): schools.proximity,
    (Theme.health, "5.1"): health.pulse,
    (Theme.health, "5.2"): health.qos,
}
