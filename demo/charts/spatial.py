"""Card 3 — Spatial & Connectivity chart builders."""
from __future__ import annotations

import math

import plotly.graph_objects as go

from ..aggregates import spatial as agg
from . import style

ACCENT = style.ACCENT["c3"]   # green — Spatial
MUTED = style.MUTED


# ────────────────────────────────────────────────────────────────────────
# 3.1 — Multi-layer spatial canvas: boarding density (hex-like density map)
# ────────────────────────────────────────────────────────────────────────
def chart_3_1_density(dark: bool = False) -> go.Figure:
    rows = agg.boarding_density_per_stop()
    hot = agg.top_hot_cells(5)
    top_share = (sum(h["boardings"] for h in hot)
                 / max(sum(r["boardings"] for r in rows), 1)) * 100
    fig = style.figure(
        title="A few central stops dominate the boarding map.",
        subtitle=f"Boarding density at every AFC-active stop, Jan–Mar 2026 · "
                 f"top-5 stops carry {top_share:.0f}% of all boardings",
        height=520, dark=dark,
    )
    fig.add_trace(go.Densitymap(
        lat=[r["lat"] for r in rows],
        lon=[r["lng"] for r in rows],
        z=[r["boardings"] for r in rows],
        radius=30,
        opacity=0.78,
        colorscale=[
            [0.0,  "rgba(47,138,79,0.0)"],
            [0.15, "rgba(47,138,79,0.55)"],
            [0.45, "rgba(217,161,44,0.85)"],
            [1.0,  "rgba(228,90,46,1.0)"],
        ],
        showscale=True,
        colorbar=dict(thickness=8, len=0.55, x=1.0,
                      tickfont=dict(family=style.FONT_MONO, size=9, color=style.INK_3),
                      title=dict(text="boardings", font=dict(family=style.FONT_MONO, size=9, color=style.INK_3))),
        hoverinfo="skip",
    ))
    # Layer: top 5 hot stops as labeled points
    fig.add_trace(go.Scattermap(
        lat=[h["lat"] for h in hot],
        lon=[h["lng"] for h in hot],
        text=[f"{h['name'][:24]}  ·  {h['boardings']:,}" for h in hot],
        marker=dict(size=12, color="#E45A2E" if dark else "#FFFFFF", opacity=1.0),
        textfont=dict(family="Open Sans Regular", size=11, color="#F4F1EC" if dark else style.INK),
        textposition="top right",
        mode="markers+text",
        customdata=[[h["name"], h["boardings"]] for h in hot],
        hovertemplate="<b>%{text}</b><extra></extra>",
        name="Top-5 stops", showlegend=True,
        meta=dict(
            entity="Stop", titleIdx=0, sub="Top boarding hot-spot",
            fields=[dict(label="Boardings (90d)", idx=1, fmt=",")],
            note="One of the five highest-volume stops in the network. Click "
                 "density cells (Phase 2) to break a hot-spot down by route.",
        ),
    ))
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", x=0, y=-0.02, yanchor="top",
                    bgcolor="rgba(10,14,21,0.6)" if dark else "rgba(255,255,255,0.85)",
                    font=dict(family=style.FONT_MONO, size=10,
                              color="#F4F1EC" if dark else style.INK_2)),
        map=dict(style="carto-darkmatter" if dark else "carto-positron",
                 center=dict(lat=10.7770, lon=106.6920),
                 zoom=10.3),
        margin=dict(l=8, r=8, t=24, b=8),
        font=dict(family="Open Sans Regular"),  # avoid CORS on CartoCDN font glyphs
    )
    return fig


# ────────────────────────────────────────────────────────────────────────
# 3.2 — Bus → Metro Sankey
# ────────────────────────────────────────────────────────────────────────
def chart_3_2_metro_sankey() -> go.Figure:
    data = agg.feeder_routes_to_metro()
    src = [l[0] for l in data["links"]]
    dst = [l[1] for l in data["links"]]
    val = [l[2] for l in data["links"]]
    feeders = data["feeder_count"]
    fig = style.figure(
        title="Many bus routes feed the Metro Line 1 corridor.",
        subtitle=f"Boardings at stops within 550 m of each Metro station, expanded to feeder routes · "
                 f"{feeders} feeder routes",
        height=540,
    )
    fig.add_trace(go.Sankey(
        node=dict(
            label=data["nodes"],
            pad=14, thickness=14,
            color=[ACCENT if "Metro" in n else (style.INK_4 if "All " in n else "#7AAB87") for n in data["nodes"]],
            line=dict(width=0),
        ),
        link=dict(
            source=src, target=dst, value=val,
            color=["rgba(47,138,79,0.30)"] * len(src),
            hovertemplate="%{source.label} → %{target.label}<br>%{value:,} boardings<extra></extra>",
        ),
        textfont=dict(family=style.FONT_MONO, size=10, color=style.INK_2),
    ))
    fig.update_layout(margin=dict(l=8, r=8, t=24, b=8))
    return fig


# ────────────────────────────────────────────────────────────────────────
# 3.4 (v5.5) — Accessibility isochrone (network-reachability proxy)
# ────────────────────────────────────────────────────────────────────────
def chart_3_4_isochrone() -> go.Figure:
    data = agg.isochrone_from_origin()
    origin = data.get("origin")
    if origin is None:
        return style.figure("Origin stop not found.", subtitle="", height=480)

    fig = style.figure(
        title="One transfer multiplies the reachable-stop count.",
        subtitle=f"Network-reachability isochrone from {origin['name'][:30]} (Phase-1 proxy over the route-sharing graph) · "
                 f"one transfer adds {data['band2_n']:,} stops · "
                 "green = no transfer · amber = one transfer",
        height=520,
    )
    # Band 2 first (amber, underneath)
    fig.add_trace(go.Scattermap(
        lat=[s["lat"] for s in data["band2"]],
        lon=[s["lng"] for s in data["band2"]],
        text=[s["name"][:32] for s in data["band2"]],
        marker=dict(size=6, color="#E8B33A", opacity=0.5),
        mode="markers", hovertemplate="<b>%{text}</b><br>one transfer<extra></extra>",
        name="One transfer (≈ ≤30 min)", showlegend=True,
    ))
    # Band 1 (green)
    fig.add_trace(go.Scattermap(
        lat=[s["lat"] for s in data["band1"]],
        lon=[s["lng"] for s in data["band1"]],
        text=[s["name"][:32] for s in data["band1"]],
        marker=dict(size=8, color="#2F8A4F", opacity=0.7),
        mode="markers", hovertemplate="<b>%{text}</b><br>no transfer<extra></extra>",
        name="No transfer (≈ ≤15 min)", showlegend=True,
    ))
    # Origin (accent star)
    fig.add_trace(go.Scattermap(
        lat=[origin["lat"]], lon=[origin["lng"]],
        text=[origin["name"]],
        marker=dict(size=16, color=ACCENT, opacity=1.0),
        mode="markers+text", textposition="top right",
        textfont=dict(family="Open Sans Regular", size=12, color=style.INK),
        hovertemplate="<b>%{text}</b><br>origin<extra></extra>",
        name="Origin stop", showlegend=True,
    ))
    fig.update_layout(
        legend=dict(orientation="h", x=0, y=-0.02, yanchor="top",
                    bgcolor="rgba(255,255,255,0.85)",
                    font=dict(family=style.FONT_MONO, size=10, color=style.INK_2)),
        showlegend=True,
        map=dict(style="carto-positron",
                 center=dict(lat=origin["lat"], lon=origin["lng"]),
                 zoom=10.6),
        margin=dict(l=8, r=8, t=24, b=8),
        font=dict(family="Open Sans Regular"),
    )
    return fig
