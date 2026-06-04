"""Card 5 — Network Health & Performance chart builders."""
from __future__ import annotations

import plotly.graph_objects as go

from .. import db
from ..aggregates import health as agg
from . import style

ACCENT = style.ACCENT["c5"]   # purple — Network Health


# ────────────────────────────────────────────────────────────────────────
# 5.1 — Network pulse with Tết anomaly (also the spine of Story 4)
# ────────────────────────────────────────────────────────────────────────
def chart_5_1_pulse(scene: str | None = None, dark: bool = False) -> go.Figure:
    """`scene` controls which story-scene overlays are drawn.
       Tet story scenes: 'tet_window', 'recovery', 'per_route', None (default).
       `dark` renders the dark-theme variant for the scrollytelling Story."""
    rows = agg.daily_volume()
    metrics = agg.tet_drop_metrics()

    if scene == "tet_window":
        title = f"Daily ridership drops {metrics['drop_pct']:.0f}% across the Tết window."
        subtitle = f"Boardings per day, Jan–Mar 2026 · Tết starts {agg.TET_2026_START}"
    elif scene == "recovery":
        title = "Recovery takes until the first week of March."
        subtitle = "Same timeline, with the recovery marker overlaid"
    elif scene == "per_route":
        title = "Some routes drop 90% during Tết, others only 30% — resilience varies."
        subtitle = "Per-route deviation from the pre-Tết baseline"
    else:
        _word = ("collapses" if metrics["drop_pct"] >= 50
                 else "dips" if metrics["drop_pct"] >= 20 else "holds steady")
        title = f"Ridership {_word} across the Tết window, then recovers."
        subtitle = (f"Boardings per day, Jan 1 – Mar 31 2026 · "
                    f"−{metrics['drop_pct']:.0f}% average, −{metrics['min_drop_pct']:.0f}% on the trough day")

    base_col = "rgba(244,241,236,0.34)" if dark else "rgba(110,118,137,0.40)"
    anno_bg = "#0A0E15" if dark else "#FFFFFF"
    grid = "rgba(255,255,255,0.06)" if dark else style.LINE
    axis = "rgba(255,255,255,0.14)" if dark else style.LINE_MD
    tick = "#5B6373" if dark else style.INK_3
    GREEN = "#3FB36B" if dark else "#2F8A4F"

    fig = style.figure(title=title, subtitle=subtitle, height=460, dark=dark)

    days = [r["day"] for r in rows]
    vals = [r["boardings"] for r in rows]
    by_day = {r["day"]: r["boardings"] for r in rows}
    start, end = agg.TET_2026_START, agg.TET_2026_END
    trough, recovery = metrics["min_day"], metrics["recovery_day"]
    pre_mean = metrics["pre_mean"]

    # Shaded Tết window (the highlight band)
    fig.add_vrect(x0=start, x1=end,
                  fillcolor=ACCENT, opacity=0.14 if dark else 0.09, line_width=0, layer="below")

    # ── Fixed 4-trace structure (kept constant across scenes so the story can
    #    smoothly morph between pulse states) ──────────────────────────────
    # 1 · the whole timeline, de-emphasised
    fig.add_trace(go.Scatter(
        x=days, y=vals, mode="lines",
        line=dict(color=base_col, width=1.6),
        hovertemplate="<b>%{x|%a %b %d}</b><br>%{y:,} boardings<extra></extra>",
        name="Daily boardings",
    ))
    # 2 · the Tết window, in focal accent (the "what dropped" highlight)
    tet_days = [d for d in days if start <= d <= end]
    fig.add_trace(go.Scatter(
        x=tet_days, y=[by_day[d] for d in tet_days], mode="lines",
        line=dict(color=ACCENT, width=3.2),
        fill="tozeroy", fillcolor="rgba(228,90,46,0.12)",
        hovertemplate="<b>%{x|%a %b %d}</b><br>%{y:,} boardings · Tết<extra></extra>",
        name="Tết window",
    ))
    # 3 · the recovery ramp, trough → baseline (shown on the recovery scene)
    rec_days = [d for d in days if trough and recovery and trough <= d <= recovery]
    fig.add_trace(go.Scatter(
        x=rec_days, y=[by_day[d] for d in rec_days], mode="lines",
        line=dict(color=GREEN, width=3.2 if scene == "recovery" else 0.1),
        opacity=1.0 if scene == "recovery" else 0.0,
        hovertemplate="<b>%{x|%a %b %d}</b><br>%{y:,} boardings · recovering<extra></extra>",
        name="Recovery", showlegend=(scene == "recovery"),
    ))
    # 4 · the January baseline, as a reference line
    fig.add_trace(go.Scatter(
        x=[days[0], days[-1]], y=[pre_mean, pre_mean], mode="lines",
        line=dict(color=tick, width=1.2, dash="dot"),
        hoverinfo="skip", name="Jan baseline",
    ))

    fig.add_annotation(
        x=start, xref="x", xanchor="left", y=1.02, yref="paper", yanchor="bottom",
        text="<b>TẾT WINDOW</b>",
        font=dict(family=style.FONT_MONO, size=10, color=ACCENT), showarrow=False,
    )

    # Trough flag — emphasised on the drop/default scenes
    if trough and scene != "recovery":
        fig.add_annotation(
            x=trough, y=metrics["min_val"],
            text=f"−{metrics['min_drop_pct']:.0f}% · {trough}",
            ax=0, ay=-46, arrowhead=2, arrowwidth=1.2, arrowcolor=ACCENT, arrowsize=0.8,
            font=dict(family=style.FONT_MONO, size=10, color="#0A0E15" if dark else "#FFFFFF"),
            bgcolor=ACCENT, bordercolor=ACCENT, borderwidth=1, borderpad=5,
        )

    if scene == "recovery" and recovery:
        fig.add_vline(x=recovery, line=dict(color=GREEN, width=1.4, dash="dash"))
        fig.add_annotation(
            x=recovery, y=pre_mean, text=f"back to baseline · {recovery}",
            ax=34, ay=-26, arrowhead=2, arrowwidth=1.2, arrowcolor=GREEN,
            font=dict(family=style.FONT_MONO, size=10, color="#0A0E15" if dark else "#FFFFFF"),
            bgcolor=GREEN, bordercolor=GREEN, borderwidth=1, borderpad=5,
        )

    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", y=1.07, x=0, yanchor="bottom",
                    font=dict(family=style.FONT_MONO, size=10, color=tick),
                    bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=False, showline=True, linecolor=axis,
                   tickfont=dict(family=style.FONT_MONO, size=10, color=tick)),
        yaxis=dict(showgrid=True, gridcolor=grid, rangemode="tozero", tickformat="~s",
                   tickfont=dict(family=style.FONT_MONO, size=10, color=tick)),
        margin=dict(l=64, r=28, t=44, b=42),
    )
    return fig


# ────────────────────────────────────────────────────────────────────────
# Story-only — fare-class collapse during Tết (Bang scene)
# ────────────────────────────────────────────────────────────────────────
def chart_tet_fareclass(dark: bool = True) -> go.Figure:
    """Daily boardings split by fare class across the Tết window, showing
    that the student fare class collapses harder and earlier than cash.
    Tier-2 story-only chart (not in the tool catalogue)."""
    rows = db.query("""
        SELECT day, fare_class, boardings FROM agg_network_day
        WHERE day BETWEEN '2026-02-01' AND '2026-03-05'
        ORDER BY day
    """)
    days = sorted({r["day"] for r in rows})
    series = {"student": {}, "cash": {}, "free": {}}
    for r in rows:
        if r["fare_class"] in series:
            series[r["fare_class"]][r["day"]] = r["boardings"]
    fig = style.figure(
        title="Student fares collapse first, and deepest.",
        subtitle="Daily boardings by fare class, 1 Feb – 5 Mar 2026 · Tết window shaded",
        height=460, dark=dark,
    )
    fig.add_vrect(x0=agg.TET_2026_START, x1=agg.TET_2026_END,
                  fillcolor=ACCENT, opacity=0.12 if dark else 0.09, line_width=0, layer="below")
    cols = {"student": "#E45A2E", "cash": "#A8AFBC" if dark else "#8C95A6",
            "free": "#6A4DB0"}
    for fc in ["cash", "student", "free"]:
        fig.add_trace(go.Scatter(
            x=days, y=[series[fc].get(d, 0) for d in days], mode="lines",
            line=dict(color=cols[fc], width=2.2 if fc == "student" else 1.6),
            name=fc, hovertemplate="<b>%{x|%b %d}</b><br>" + fc + " %{y:,}<extra></extra>",
        ))
    tick = "#5B6373" if dark else style.INK_3
    axis = "rgba(255,255,255,0.14)" if dark else style.LINE_MD
    grid = "rgba(255,255,255,0.06)" if dark else style.LINE
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", y=1.06, x=0, font=dict(family=style.FONT_MONO, size=10, color=tick)),
        xaxis=dict(showgrid=False, showline=True, linecolor=axis,
                   tickfont=dict(family=style.FONT_MONO, size=10, color=tick)),
        yaxis=dict(showgrid=True, gridcolor=grid, rangemode="tozero", tickformat="~s",
                   tickfont=dict(family=style.FONT_MONO, size=10, color=tick)),
        margin=dict(l=64, r=28, t=28, b=42),
    )
    return fig


# ────────────────────────────────────────────────────────────────────────
# 5.2 — QoS small-multiples scatter (v5.5 front door · 3 mini-scatters)
# ────────────────────────────────────────────────────────────────────────
def chart_5_2_qos_small_multiples() -> go.Figure:
    from plotly.subplots import make_subplots
    rows = agg.qos_small_multiples(60)
    rows = sorted(rows, key=lambda r: -r["total"])
    x = list(range(1, len(rows) + 1))
    dims = [
        ("qos1", "QoS-1 · trip completion (proxy)"),
        ("qos2", "QoS-2 · on-path (proxy)"),
        ("qos3", "QoS-3 · on-schedule (proxy)"),
    ]
    fig = make_subplots(rows=1, cols=3, subplot_titles=[d[1] for d in dims],
                        horizontal_spacing=0.06)
    cd = [[f"Route {r['route_no']}", r["qos1"], r["qos2"], r["qos3"], r["total"]] for r in rows]
    panel_meta = dict(
        entity="Route", titleIdx=0, sub="QoS proxy scores (Phase 1)",
        fields=[
            dict(label="QoS-1 · completion", idx=1, fmt="%"),
            dict(label="QoS-2 · on-path", idx=2, fmt="%"),
            dict(label="QoS-3 · on-schedule", idx=3, fmt="%"),
            dict(label="Boardings (90d)", idx=4, fmt=","),
        ],
        note="Phase-1 fare-event proxies for the three Chawuthai 2023 QoS tiers; "
             "true GPS-based QoS awaits the full 50-day window.",
    )
    for i, (key, _) in enumerate(dims, start=1):
        vals = [r[key] for r in rows]
        fig.add_trace(go.Scatter(
            x=x, y=vals, mode="markers",
            marker=dict(size=7, color=vals,
                        colorscale=[[0.0, "#C03A3A"], [0.5, "#E8B33A"], [1.0, ACCENT]],
                        cmin=0, cmax=100,
                        showscale=(i == 3),
                        colorbar=dict(thickness=8, len=0.7, x=1.005, title=dict(
                            text="score", font=dict(family=style.FONT_MONO, size=9, color=style.INK_3)),
                            tickfont=dict(family=style.FONT_MONO, size=9, color=style.INK_3)) if i == 3 else None,
                        opacity=0.8, line=dict(width=0)),
            customdata=cd,
            hovertemplate="%{customdata[0]}<br>" + key.upper() + " %{y:.0f}<extra></extra>",
            showlegend=False,
            meta=panel_meta,
        ), row=1, col=i)
        fig.update_yaxes(range=[0, 100], showgrid=True, gridcolor=style.LINE,
                         tickfont=dict(family=style.FONT_MONO, size=9, color=style.INK_3), row=1, col=i)
        fig.update_xaxes(showticklabels=False, showgrid=False,
                         title=dict(text="routes by volume", font=dict(family=style.FONT_MONO, size=9, color=style.INK_4)),
                         row=1, col=i)
    fig.update_layout(
        template="simple_white", paper_bgcolor=style.SURFACE, plot_bgcolor=style.SURFACE,
        font=dict(family=style.FONT_SANS, size=12, color=style.INK_2),
        margin=dict(l=44, r=20, t=44, b=40),
        autosize=True, showlegend=False,
        meta=dict(action_title="Reliability decomposes into three dimensions, and the weakest one differs by route."),
    )
    for ann in fig.layout.annotations:
        ann.font = dict(family=style.FONT_MONO, size=10, color=style.INK_2)
    return fig


# ────────────────────────────────────────────────────────────────────────
# 5.x — Service-day calendar (cut from v5.5; retained as a builder)
# ────────────────────────────────────────────────────────────────────────
def chart_5_2_calendar() -> go.Figure:
    rows = agg.service_calendar()
    if not rows:
        return style.figure("Calendar unavailable", subtitle="", height=380)
    weeks = sorted({r["iso_week"] for r in rows})
    dow_lbl = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    z = [[None] * len(weeks) for _ in range(7)]
    days_grid = [[""] * len(weeks) for _ in range(7)]
    week_idx = {w: i for i, w in enumerate(weeks)}
    for r in rows:
        z[r["dow"]][week_idx[r["iso_week"]]] = r["boardings"]
        days_grid[r["dow"]][week_idx[r["iso_week"]]] = r["day"]

    fig = style.figure(
        title="Sundays are the quietest day-of-week — except during Tết, when every day is empty.",
        subtitle="Daily boardings laid out as ISO week (column) × day-of-week (row), Jan–Mar 2026",
        height=420,
    )
    fig.add_trace(go.Heatmap(
        z=z,
        x=[f"W{w:02d}" for w in weeks],
        y=dow_lbl,
        customdata=days_grid,
        colorscale=[
            [0.0, "#F3F0FA"],
            [0.25, "#C4B5E8"],
            [0.6, "#8869C0"],
            [1.0, ACCENT],
        ],
        showscale=True,
        colorbar=dict(thickness=8, len=0.55, x=1.01,
                      tickfont=dict(family=style.FONT_MONO, size=9, color=style.INK_3),
                      title=dict(text="boardings", font=dict(family=style.FONT_MONO, size=9, color=style.INK_3))),
        hovertemplate="<b>%{customdata}</b><br>%{z:,} boardings<extra></extra>",
        xgap=2, ygap=2,
    ))
    fig.update_layout(
        xaxis=dict(side="bottom", showgrid=False, showline=False, ticks="",
                   tickfont=dict(family=style.FONT_MONO, size=10, color=style.INK_3)),
        yaxis=dict(autorange="reversed", showgrid=False, showline=False, ticks="",
                   tickfont=dict(family=style.FONT_MONO, size=10, color=style.INK_3)),
        margin=dict(l=60, r=90, t=28, b=40),
    )
    return fig


# ────────────────────────────────────────────────────────────────────────
# 5.3 — Reliability scorecard (Phase 1 proxy QoS)
# ────────────────────────────────────────────────────────────────────────
def chart_5_3_scorecard() -> go.Figure:
    rows = agg.reliability_scorecard(25)
    rows = sorted(rows, key=lambda r: r["consistency"], reverse=True)
    routes = [f"Rt {r['route_no']}" for r in rows]
    consistency = [r["consistency"] for r in rows]
    fig = style.figure(
        title="Top-25 most-reliable routes by hourly consistency (Phase 1 proxy).",
        subtitle="True QoS-1/2/3 awaits the full 50-day GPS pull · this proxy uses fare-event variance",
        height=520,
    )
    fig.add_trace(go.Bar(
        x=consistency,
        y=routes,
        orientation="h",
        marker=dict(color=ACCENT),
        text=[f"{c*100:.0f}%" for c in consistency],
        textposition="outside",
        textfont=dict(family=style.FONT_MONO, size=10, color=style.INK_2),
        customdata=[[f"Route {r['route_no']}", r["consistency"] * 100] for r in rows],
        hovertemplate="<b>%{y}</b><br>consistency %{x:.2%}<extra></extra>",
        meta=dict(
            entity="Route", titleIdx=0, sub="Reliability proxy (Phase 1)",
            fields=[dict(label="Hourly consistency", idx=1, fmt="%1")],
            note="Phase-1 proxy = 1 − (std/mean) of hourly boardings. True "
                 "QoS-1/2/3 (Chawuthai 2023) awaits the full 50-day GPS pull.",
        ),
    ))
    fig.update_layout(
        xaxis=dict(rangemode="tozero", showgrid=True, gridcolor=style.LINE,
                   tickformat=".0%",
                   tickfont=dict(family=style.FONT_MONO, size=10, color=style.INK_3)),
        yaxis=dict(autorange="reversed",
                   tickfont=dict(family=style.FONT_MONO, size=10, color=style.INK)),
        bargap=0.25,
        margin=dict(l=88, r=80, t=28, b=36),
    )
    return fig
