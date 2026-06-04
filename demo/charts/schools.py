"""Card 2 — School-Aware Demand chart builders (Plotly).

Every builder consumes one aggregate from demo.aggregates.schools and returns
a Plotly figure constructed through demo.charts.style.figure() so the A2/A4/A5
visual invariants are applied uniformly.
"""
from __future__ import annotations

import plotly.graph_objects as go

from ..aggregates import schools as agg
from . import style

ACCENT = style.ACCENT["c2"]   # gold — School flagship
MUTED = style.MUTED


# ────────────────────────────────────────────────────────────────────────
# 2.1 — School constellation (bubble scatter) · v5.5 front door
#   X = student boardings · Y = morning-peak share · size = serving routes
#   colour = equity (nearby stops within 500 m), gradient
# ────────────────────────────────────────────────────────────────────────
def chart_2_1_constellation() -> go.Figure:
    data = agg.school_constellation()
    if not data:
        return style.figure("No school catchment data.", subtitle="", height=440)
    xs = [r["student_boardings"] for r in data]
    ys = [r["morning_peak_share"] * 100 for r in data]
    sizes = [r["serving_routes"] for r in data]
    equity = [r["nearby_stops"] for r in data]
    labels = [r["display"] for r in data]
    routes_by_slug = agg.school_serving_routes()
    serving = [[[e["route_no"], e["student_boardings"]] for e in routes_by_slug.get(r["slug"], [])]
               for r in data]

    max_routes = max(sizes) or 1
    # bubble radius 14–46 px scaled by serving routes
    radii = [14 + 32 * (s / max_routes) for s in sizes]

    fig = style.figure(
        title="Boarding volume and morning-peak share, by university.",
        subtitle="X = 90-day student-fare boardings · Y = share in the 6–8 AM peak · "
                 "bubble size = serving routes · colour = stops within 500 m (equity)",
        height=460,
    )
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="markers+text",
        text=labels, textposition="top center",
        textfont=dict(family=style.FONT_MONO, size=10, color=style.INK_2),
        marker=dict(
            size=radii,
            color=equity,
            colorscale=[[0.0, "#C03A3A"], [0.4, "#E8B33A"], [1.0, ACCENT]],
            showscale=True,
            colorbar=dict(thickness=8, len=0.5, x=1.0,
                          title=dict(text="stops<br>≤500m", font=dict(family=style.FONT_MONO, size=9, color=style.INK_3)),
                          tickfont=dict(family=style.FONT_MONO, size=9, color=style.INK_3)),
            line=dict(width=1.5, color="#FFFFFF"),
            opacity=0.9,
        ),
        customdata=[[r["student_boardings"], r["serving_routes"], r["nearby_stops"],
                     r["morning_peak_share"] * 100, r["display"], serving[i]]
                    for i, r in enumerate(data)],
        hovertemplate="<b>%{text}</b><br>%{customdata[0]:,} student boardings<br>"
                      "%{y:.0f}% in morning peak<br>%{customdata[1]} serving routes<br>"
                      "%{customdata[2]} stops within 500 m<extra></extra>",
        meta=dict(
            entity="University", titleIdx=4,
            sub="School ridership profile",
            fields=[
                dict(label="Student boardings (90d)", idx=0, fmt=","),
                dict(label="Morning-peak share", idx=3, fmt="%"),
                dict(label="Serving routes", idx=1, fmt=""),
                dict(label="Stops within 500 m", idx=2, fmt=""),
            ],
            list=dict(idx=5, label="Top serving routes", unit="student boardings"),
            note="Bubble size encodes serving routes; colour encodes the count "
                 "of stops in the 500 m walking catchment (equity).",
        ),
    ))
    fig.update_layout(
        xaxis=dict(title=dict(text="Student-fare boardings (90 d)", font=dict(family=style.FONT_MONO, size=10, color=style.INK_3)),
                   showgrid=True, gridcolor=style.LINE, rangemode="tozero",
                   tickformat="~s",
                   tickfont=dict(family=style.FONT_MONO, size=10, color=style.INK_3)),
        yaxis=dict(title=dict(text="Morning-peak share (%)", font=dict(family=style.FONT_MONO, size=10, color=style.INK_3)),
                   showgrid=True, gridcolor=style.LINE, rangemode="tozero",
                   tickfont=dict(family=style.FONT_MONO, size=10, color=style.INK_3)),
        margin=dict(l=64, r=80, t=28, b=48),
    )
    return fig


# ────────────────────────────────────────────────────────────────────────
# 2.2 — Schools → Routes treemap (flagship)
# ────────────────────────────────────────────────────────────────────────
def chart_2_2_treemap() -> go.Figure:
    rows = agg.schools_to_routes_treemap()
    uni_by_slug = {u["slug"]: u for u in agg.UNIVERSITIES}

    # Bucket: uni_name → list of (route_no, student_boardings)
    per_uni: dict[str, list[dict]] = {}
    for r in rows:
        uni = uni_by_slug.get(r["uni_slug"])
        if uni is None:
            continue
        per_uni.setdefault(uni["display"], []).append(r)

    # Build with explicit ids so labels can repeat across universities and so
    # the "+N routes" node is a real branch the reader can click to drill into.
    ids: list[str] = []
    labels: list[str] = []
    parents: list[str] = []
    values: list[int] = []
    colours: list[str] = []

    # Headline finding text computed from data
    biggest_route = None
    biggest_uni = None
    biggest_val = 0

    for uni_name, edges in per_uni.items():
        uid = f"uni::{uni_name}"
        ids.append(uid); labels.append(uni_name); parents.append("")
        values.append(0); colours.append("#3A4256")

        edges_sorted = sorted(edges, key=lambda e: e["student_boardings"], reverse=True)
        top = edges_sorted[:4]
        rest = edges_sorted[4:]
        for e in top:
            ids.append(f"{uid}::rt::{e['route_no']}")
            labels.append(f"Route {e['route_no']}")
            parents.append(uid)
            values.append(e["student_boardings"])
            colours.append(ACCENT)
            if e["student_boardings"] > biggest_val:
                biggest_val = e["student_boardings"]
                biggest_route = e["route_no"]
                biggest_uni = uni_name
        if rest:
            rest_id = f"{uid}::rest"
            ids.append(rest_id)
            labels.append(f"+{len(rest)} routes")
            parents.append(uid)
            values.append(0)
            colours.append(MUTED)
            for e in rest:
                ids.append(f"{rest_id}::{e['route_no']}")
                labels.append(f"Route {e['route_no']}")
                parents.append(rest_id)
                values.append(e["student_boardings"])
                colours.append("#C7B36A")

    # Data-driven, number-free action title: do students bunch onto a few
    # routes per campus, or spread out? Decided by the average top-route share.
    _shares = []
    for _edges in per_uni.values():
        _tot = sum(e["student_boardings"] for e in _edges)
        if _tot:
            _shares.append(max(e["student_boardings"] for e in _edges) / _tot)
    _concentrated = bool(_shares) and (sum(_shares) / len(_shares) >= 0.30)
    _ = (biggest_route, biggest_uni, biggest_val)  # retained for hover/debug
    fig = style.figure(
        title=("Each university's student ridership concentrates on a few routes."
               if _concentrated else
               "Each university's student ridership spreads across many routes."),
        subtitle="Sized by 90-day student-fare boardings in the 500 m walking catchment of each campus",
        height=460,
    )
    fig.add_trace(go.Treemap(
        ids=ids, labels=labels, parents=parents, values=values,
        branchvalues="remainder",   # parent value (0) adds to children sum
        maxdepth=2,                 # show uni + its routes; "+N routes" drills deeper
        marker=dict(colors=colours, line=dict(width=2, color="#FFFFFF")),
        textfont=dict(family=style.FONT_DISPLAY, size=14, color="#FFFFFF"),
        textposition="middle center",
        hovertemplate="<b>%{label}</b><br>%{value:,} student boardings<extra></extra>",
    ))
    fig.update_layout(margin=dict(l=8, r=8, t=24, b=8))
    return fig


# ────────────────────────────────────────────────────────────────────────
# 2.3 — Weekly fare-class heatmap (hour × day-of-week)
# ────────────────────────────────────────────────────────────────────────
def chart_2_3_weekly(segment: str = "student", date_from: str | None = None,
                     date_to: str | None = None, route: str = "",
                     day_type: str = "all") -> go.Figure:
    rows = agg.weekly_heatmap(segment, date_from, date_to, route, day_type)
    dow_lbl = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    z = [[0] * 24 for _ in range(7)]
    for r in rows:
        z[r["dow"]][r["hour"]] = r["boardings"]

    title_for = {
        "student":     "Student boardings concentrate in weekday peak hours.",
        "non_student": "Non-student boardings are spread across the day.",
        "all":         "The network pulses with a sharp morning and evening peak.",
        "free":        "Free-fare rides cluster on weekend afternoons.",
    }
    fig = style.figure(
        title=title_for.get(segment, "Weekly ridership by hour"),
        subtitle="Boardings by hour-of-day × day-of-week · " + segment.replace("_", " ") + " fare · Jan–Mar 2026",
        height=420,
    )
    fig.add_trace(go.Heatmap(
        z=z,
        x=[f"{h:02d}" for h in range(24)],
        y=dow_lbl,
        colorscale=[
            [0.0, "#FFFAEB"],
            [0.15, "#FFE9B0"],
            [0.45, "#E8B33A"],
            [1.0, ACCENT],
        ],
        showscale=True,
        colorbar=dict(
            thickness=8, len=0.55, x=1.01, xanchor="left",
            tickfont=dict(family=style.FONT_MONO, size=9, color=style.INK_3),
            title=dict(text="boardings", font=dict(family=style.FONT_MONO, size=9, color=style.INK_3)),
        ),
        hovertemplate="<b>%{y} %{x}:00</b><br>%{z:,} boardings<extra></extra>",
    ))
    fig.update_layout(
        xaxis=dict(side="bottom", showgrid=False, showline=False, ticks="",
                   tickfont=dict(family=style.FONT_MONO, size=10, color=style.INK_3)),
        yaxis=dict(autorange="reversed", showgrid=False, showline=False, ticks="",
                   tickfont=dict(family=style.FONT_MONO, size=10, color=style.INK_3)),
        margin=dict(l=60, r=90, t=24, b=40),
    )
    return fig


# ────────────────────────────────────────────────────────────────────────
# 2.4 — School proximity & equity (point map on HCMC bbox)
# ────────────────────────────────────────────────────────────────────────
def chart_2_4_proximity() -> go.Figure:
    rows = agg.school_proximity_geo()
    base = agg.all_stops_geo()
    catch = agg.catchment_stops_geo()

    fig = style.figure(
        title="Most universities sit on a dense stop cluster — but coverage is uneven.",
        subtitle="Every city stop (grey), the 500 m walking catchment of each campus (gold), "
                 "and the eight verified universities",
        height=440,
    )
    # Layer 1 — every stop, faint, to give the map its city shape
    fig.add_trace(go.Scattermap(
        lat=[r["lat"] for r in base],
        lon=[r["lng"] for r in base],
        marker=dict(size=4, color="#9AA3B2", opacity=0.35),
        mode="markers", hoverinfo="skip",
        name="All stops", showlegend=True,
    ))
    # Layer 2 — stops inside a campus walking catchment
    fig.add_trace(go.Scattermap(
        lat=[r["lat"] for r in catch],
        lon=[r["lng"] for r in catch],
        marker=dict(size=7, color="#E8B33A", opacity=0.85),
        mode="markers",
        hovertemplate="Stop in campus catchment<extra></extra>",
        name="Catchment stop (≤500 m)", showlegend=True,
    ))
    # Layer 3 — the universities themselves
    fig.add_trace(go.Scattermap(
        lat=[r["lat"] for r in rows],
        lon=[r["lng"] for r in rows],
        text=[r["display"] for r in rows],
        marker=dict(
            size=[16 + 1.4 * r["nearby_stops"] for r in rows],
            color=[ACCENT if r["verified"] else "#C03A3A" for r in rows],
            opacity=0.95,
        ),
        mode="markers+text",
        textfont=dict(family="Open Sans Regular", size=11, color=style.INK),
        textposition="top right",
        customdata=[[r["display"], r["nearby_stops"],
                     "verified" if r["verified"] else "district-level",
                     [[e["route_no"], e["student_boardings"]]
                      for e in agg.school_serving_routes().get(r["slug"], [])]]
                    for r in rows],
        hovertemplate="<b>%{text}</b><br>%{customdata[1]} stops within 500 m<extra></extra>",
        name="University", showlegend=True,
        meta=dict(
            entity="University", titleIdx=0,
            sub="Stop-coverage / equity",
            fields=[
                dict(label="Stops within 500 m", idx=1, fmt=""),
                dict(label="Geocoding", idx=2, fmt=""),
            ],
            list=dict(idx=3, label="Top serving routes", unit="student boardings"),
            note="Verified universities are hand-geocoded to their main-gate stop; "
                 "the rest are placed at district granularity (Phase 2 backfill).",
        ),
    ))
    fig.update_layout(
        legend=dict(orientation="h", x=0, y=-0.02, yanchor="top",
                    bgcolor="rgba(255,255,255,0.85)",
                    font=dict(family=style.FONT_MONO, size=10, color=style.INK_2)),
        showlegend=True,
        map=dict(
            style="carto-positron",
            center=dict(lat=10.7770, lon=106.6920),
            zoom=10.3,
        ),
        margin=dict(l=8, r=8, t=24, b=8),
        font=dict(family="Open Sans Regular"),
    )
    return fig
