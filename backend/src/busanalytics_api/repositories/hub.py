"""Hub KPI repository (Gold: agg_hub_kpis)."""
from __future__ import annotations

import decimal
from typing import Any

from .. import db


def hub_kpis() -> dict[str, Any]:
    row = db.query_one("SELECT * FROM agg_hub_kpis")
    if row is None:
        return {}
    return {k: (float(v) if isinstance(v, decimal.Decimal) else v) for k, v in row.items()}
