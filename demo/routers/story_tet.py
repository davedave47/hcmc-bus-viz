"""Story 4 — 'Nine days without a network' (Tết).

Light full-scene scrollytelling, matching the rest of the app's theme.
Seven scenes: Bing hero → five Bang chart scenes → Bongo recap+CTA.
Each Bang scene pins a light-themed Plotly chart with on-chart annotation;
Scrollama drives the progress dots, the scene-reveal fade, and the
chart mount as each scene enters the viewport.

Scene set (richer than the 6-scene Ch4.6 table — adds the fare-class
collapse scene):
  Bi  hero KPI: −84% on the trough day
  B1  pulse · Tết window highlight
  B2  pulse · trough callout
  B3  fare-class collapse (student vs cash vs free)   [Tier-2 story chart]
  B4  pulse · recovery marker
  B5  spatial resilience (dark hex map)
  Bo  recap + CTA
"""
from __future__ import annotations

import datetime
import json

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ..aggregates import health as agg
from ..charts import health as health_charts
from ..charts import spatial as spatial_charts

router = APIRouter(prefix="/cards/health/story")


def _d(iso: str, fmt: str = "%-d %B") -> str:
    """Format an ISO date string for narration ('2026-02-14' → '14 February')."""
    try:
        return datetime.date.fromisoformat(iso).strftime(fmt)
    except (ValueError, TypeError):
        return iso


def scene_data() -> list[dict]:
    m = agg.tet_drop_metrics()
    pre = m["pre_mean"]
    start, end = agg.TET_2026_START, agg.TET_2026_END
    trough, recovery = m["min_day"], m["recovery_day"]
    return [
        dict(id="bi", act="Story · Network Health",
             act_meta=f"· {_d(start, '%b %-d')} to {_d(recovery, '%b %-d')} 2026",
             kind="bing",
             h1="An 84% ridership collapse<br>over <em>nine days</em>.",
             lede="For the Lunar New Year, Hồ Chí Minh City's bus system went quiet. Then it came back. <em>This is the curve of how it happened.</em>",
             kpi=f"−{m['min_drop_pct']:.0f}%",
             kpi_l="DAILY RIDERSHIP ON THE TROUGH DAY",
             kpi_d=f"measured on {_d(trough)} against the ~{pre:,}/day January baseline."),

        dict(id="b1", act="Scene 01", act_meta="· the drop", kind="bang",
             h2=f"Ridership held steady through January.<br>Then <em>{_d(start)}</em>.",
             lede="Daily boardings for the whole network across the 90-day AFC window. Notice the cliff at the Tết window.",
             chart="pulse:tet_window",
             chart_title=f"Tết cut daily ridership by {m['drop_pct']:.0f}% across {m['window_days']} days.",
             chart_meta="All routes · Jan 1 – Mar 31 2026 · AFC",
             chart_sub=f"The shaded band is the Tết window ({_d(start, '%-d')}–{_d(end)})."),

        dict(id="b2", act="Scene 02", act_meta="· the floor", kind="bang",
             h2=f"The floor: <em>{_d(trough)}</em>.",
             lede=f"At the trough, only {m['min_val']:,} boardings crossed the scanners network-wide, about a sixth of a normal weekday.",
             chart="pulse:default",
             chart_title=f"The deepest day fell {m['min_drop_pct']:.0f}% below the January baseline.",
             chart_meta="All routes · trough annotated · AFC",
             chart_sub="The orange flag marks the single deepest day of the shock."),

        dict(id="b3", act="Scene 03", act_meta="· who vanished", kind="bang",
             h2="Students vanished <em>first</em>.",
             lede="Splitting the curve by fare class shows the student fare collapsing harder and earlier than cash; the universities emptied before the city did.",
             chart="fareclass",
             chart_title="Student fares collapse first, and deepest.",
             chart_meta="By fare class · 1 Feb – 5 Mar · AFC",
             chart_sub="Student (orange) drops to near zero; cash (grey) holds a thin floor."),

        dict(id="b4", act="Scene 04", act_meta="· the return", kind="bang",
             h2=f"Recovery took until <em>{_d(recovery)}</em>.",
             lede=f"The shock was deep but not instant to undo. Ridership climbed back through late February and returned to the January baseline on {_d(recovery)}.",
             chart="pulse:recovery",
             chart_title=f"Back to the January baseline by {_d(recovery)}.",
             chart_meta="All routes · recovery marker · AFC",
             chart_sub="The green marker is the first day back at the January baseline."),

        dict(id="b5", act="Scene 05", act_meta="· what held", kind="bang",
             h2="The routes that held share <em>airport corridors</em>.",
             lede="Switching from the time axis to the map: the densest surviving ridership clusters along the inter-province and airport corridors, while inner-city school routes fell furthest.",
             chart="spatial",
             chart_title="Where ridership concentrated through the shock.",
             chart_meta="Boarding density · all stops · AFC",
             chart_sub="Brighter cells kept more of their normal ridership."),

        dict(id="bo", act="What next", act_meta="· the call to action", kind="bongo",
             h1="Ridership stayed low nine days;<br>nine routes <em>worst affected</em>.",
             lede="Tết is a natural experiment in network shock: annual, predictable, and visible in advance. The same lens applies to the April 30 parade and to weather events once the GPS window arrives. <em>The Network Health card is where to start.</em>"),
    ]


def _chart_json(spec: str) -> str:
    if spec == "fareclass":
        return health_charts.chart_tet_fareclass(dark=False).to_json()
    if spec == "spatial":
        return spatial_charts.chart_3_1_density(dark=False).to_json()
    if spec.startswith("pulse:"):
        _, scene = spec.split(":", 1)
        sc = None if scene == "default" else scene
        return health_charts.chart_5_1_pulse(sc, dark=False).to_json()
    return ""


@router.get("/tet", response_class=HTMLResponse)
async def story_tet(request: Request):
    scenes = scene_data()
    specs = {s["chart"] for s in scenes if s.get("chart")}
    chart_bundle = {sp: _chart_json(sp) for sp in specs}
    return request.app.state.templates.TemplateResponse(
        request, "story_tet.html",
        {"scenes": scenes,
         "n_scenes": len(scenes),
         "scenes_json": json.dumps(scenes),
         "chart_bundle_json": json.dumps(chart_bundle)},
    )
