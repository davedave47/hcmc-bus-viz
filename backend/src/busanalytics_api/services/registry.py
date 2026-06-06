"""Chart registry — (theme, slug) → service.

Open/closed: add a chart by registering its service here; the router never changes.
"""
from __future__ import annotations

from collections.abc import Callable

from ..schemas import ChartResponse
from .charts import health

CHART_SERVICES: dict[tuple[str, str], Callable[[], ChartResponse]] = {
    ("health", "5.1"): health.pulse,
    ("health", "5.2"): health.qos,
}
