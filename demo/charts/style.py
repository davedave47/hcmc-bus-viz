"""Knaflic-discipline Plotly defaults.

Codifies the visual invariants from §4.8 of the report:
  A2  action title + supporting subtitle (title states the finding;
        subtitle does the labelling)
  A4  bar charts have zero baseline (no truncated y-axes on length encodings)
  A5  3–8 second readability (muted defaults, one accent colour for the
        focal element, direct labels when ≤ 5 categories)

Every chart in the demo composes its figure through `figure(title, subtitle, ...)`
and reads its accent colour from the per-card palette. The accent is meaningful;
the rest is intentionally muted grey.
"""
from __future__ import annotations

import plotly.graph_objects as go

# Mirror the CSS tokens for consistency between SVG/HTML chrome and Plotly
INK = "#1B2333"
INK_2 = "#3A4256"
INK_3 = "#6E7689"
INK_4 = "#A8B0C0"
LINE = "#E5E8EA"
LINE_MD = "#CCD2D6"
SURFACE = "#FFFFFF"
SURFACE_3 = "#F4F6F2"
MUTED = "#C7CDD3"      # default fill for non-focal categorical bars / lines

# Per-card accents
ACCENT = {
    "c1": "#E45A2E",  # orange — Demand
    "c2": "#B8920A",  # gold — School (flagship)
    "c3": "#2F8A4F",  # green — Spatial
    "c4": "#C03A3A",  # red — Financial
    "c5": "#6A4DB0",  # purple — Network Health
    "c6": "#334155",  # slate — Routes
}

FONT_DISPLAY = '"Funnel Display", system-ui, sans-serif'
FONT_SANS = '"Geist", system-ui, sans-serif'
FONT_MONO = '"Geist Mono", ui-monospace, monospace'


def figure(
    title: str,
    subtitle: str,
    *,
    height: int | None = None,
    show_legend: bool = False,
    dark: bool = False,
) -> go.Figure:
    """Return a Plotly figure with our locked defaults.

    The action title (the finding) and the supporting subtitle are rendered
    by the bottom caption block in the card template — NOT in the chart
    itself, to avoid duplication. We keep title/subtitle as fields on the
    figure metadata for hover summary, but suppress the rendered title.

    Pass dark=True for the scrollytelling Story (dark theme): transparent
    paper so the chart sits on the dark scene, cream text, faint gridlines.
    """
    paper = "rgba(0,0,0,0)" if dark else SURFACE
    plot = "rgba(0,0,0,0)" if dark else SURFACE
    txt = "#A8AFBC" if dark else INK_2
    tick = "#5B6373" if dark else INK_3
    grid = "rgba(255,255,255,0.06)" if dark else LINE
    line = "rgba(255,255,255,0.14)" if dark else LINE_MD
    fig = go.Figure()
    fig.update_layout(
        template="simple_white",
        paper_bgcolor=paper,
        plot_bgcolor=plot,
        font=dict(family=FONT_SANS, size=12, color=txt),
        margin=dict(l=56, r=28, t=24, b=40),
        autosize=True,
        showlegend=show_legend,
        legend=dict(
            font=dict(family=FONT_MONO, size=10, color=tick),
            bgcolor=paper, bordercolor=grid, borderwidth=0,
        ),
        hoverlabel=dict(
            bgcolor="#0A0E15" if dark else INK,
            bordercolor="#E45A2E" if dark else INK,
            font=dict(family=FONT_SANS, size=12, color="#FFFFFF"),
        ),
        xaxis=dict(
            showgrid=False, showline=True, linecolor=line,
            ticks="outside", tickcolor=line,
            tickfont=dict(family=FONT_MONO, size=10, color=tick), title=None,
        ),
        yaxis=dict(
            showgrid=True, gridcolor=grid, gridwidth=1,
            showline=False, zeroline=False,
            tickfont=dict(family=FONT_MONO, size=10, color=tick), title=None,
        ),
    )
    # Note: do NOT set layout.height — let the container drive height.
    _ = height  # unused; kept in signature for back-compat
    # Carry the action title + subtitle as figure metadata so the card header
    # renders the *computed* (data-driven) title, never a hard-coded string.
    fig.update_layout(meta=dict(action_title=title, action_sub=subtitle))
    return fig


def bar_zero_baseline(fig: go.Figure, orientation: str = "v") -> None:
    """Enforce A4: bar charts start the value axis at zero.

    Call AFTER adding the data trace(s); we read the data to compute a
    headroom and set rangemode='tozero'."""
    axis = "yaxis" if orientation == "v" else "xaxis"
    fig.update_layout(**{axis: dict(**fig.layout[axis].to_plotly_json(), rangemode="tozero")})


def action_title(fig: go.Figure, default: str = "") -> str:
    """Read the data-driven action title a builder stashed in layout.meta.
    Falls back to `default` so the card always has a header."""
    meta = fig.layout.meta
    if isinstance(meta, dict):
        return meta.get("action_title") or default
    return default


def to_json(fig: go.Figure) -> str:
    """Serialise to the JSON shape Plotly.js consumes via `Plotly.newPlot`."""
    return fig.to_json()
