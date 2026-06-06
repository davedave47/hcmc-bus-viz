"""Hub KPI repository (Gold: agg_hub_kpis)."""
from __future__ import annotations

import decimal
from typing import Any

from ..db import Warehouse


def hub_kpis(wh: Warehouse) -> dict[str, Any]:
    row = wh.query_one("SELECT * FROM agg_hub_kpis")
    if row is None:
        return {}
    return {k: (float(v) if isinstance(v, decimal.Decimal) else v) for k, v in row.items()}
