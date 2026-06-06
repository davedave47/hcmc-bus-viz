"""Network Health chart services — compute the series + A2 action title from
repository data. Framework-agnostic (no FastAPI, no Plotly)."""
from __future__ import annotations

from typing import Any

from ...db import Warehouse
from ...repositories import health as repo
from ...schemas import ChartResponse


def _drop_metrics(rows: list[dict[str, Any]], window: dict[str, Any]) -> dict[str, Any]:
    """Pre-Tết baseline vs Tết-window means, the trough day, and drop percentages."""
    by_day = {r["day"]: r["boardings"] for r in rows}
    pre = [d for d in by_day if window["pre_start"] <= d <= window["pre_end"]]
    tet = [d for d in by_day if window["tet_start"] <= d <= window["tet_end"]]
    if not pre or not tet:
        return {"pre_mean": 0, "drop_pct": 0.0, "min_day": None, "min_val": 0, "min_drop_pct": 0.0}
    pre_mean = sum(by_day[d] for d in pre) / len(pre)
    tet_mean = sum(by_day[d] for d in tet) / len(tet)
    drop_pct = 100 * (1 - tet_mean / pre_mean) if pre_mean else 0.0
    min_day = min(tet, key=lambda d: by_day[d])
    min_val = by_day[min_day]
    min_drop = 100 * (1 - min_val / pre_mean) if pre_mean else 0.0
    return {
        "pre_mean": int(pre_mean),
        "drop_pct": drop_pct,
        "min_day": min_day,
        "min_val": int(min_val),
        "min_drop_pct": min_drop,
    }


def pulse(wh: Warehouse) -> ChartResponse:
    """5.1 — Network pulse with the Tết anomaly band."""
    rows = repo.daily_volume(wh)
    window = repo.tet_window(wh)
    m = _drop_metrics(rows, window)
    word = "collapses" if m["drop_pct"] >= 50 else "dips" if m["drop_pct"] >= 20 else "holds steady"
    title = f"Ridership {word} across the Tết window, then recovers."
    subtitle = (
        f"Boardings per day, Jan 1 – Mar 31 2026 · "
        f"−{m['drop_pct']:.0f}% average, −{m['min_drop_pct']:.0f}% on the trough day"
    )
    return ChartResponse(
        theme="health",
        slug="5.1",
        title=title,
        subtitle=subtitle,
        series=rows,
        encoding={"x": "day", "y": "boardings", "kind": "timeline"},
        meta={
            "tet_start": window.get("tet_start"),
            "tet_end": window.get("tet_end"),
            "trough": m["min_day"],
            "baseline": m["pre_mean"],
            "drop_pct": round(m["drop_pct"], 1),
            "min_drop_pct": round(m["min_drop_pct"], 1),
        },
    )


def qos(wh: Warehouse) -> ChartResponse:
    """5.2 — QoS small-multiples (three proxy dimensions per route)."""
    rows = repo.qos_small_multiples(wh, 60)
    return ChartResponse(
        theme="health",
        slug="5.2",
        title="Reliability decomposes into three dimensions, and the weakest one differs by route.",
        subtitle="QoS proxy scores per route (Phase-1 fare-event proxies)",
        series=rows,
        encoding={"dims": ["qos1", "qos2", "qos3"], "size": "total", "kind": "small_multiples"},
        meta={
            "note": "Phase-1 fare-event proxies for the three Chawuthai 2023 QoS tiers; "
            "true GPS-based QoS awaits the full 50-day window.",
        },
    )
