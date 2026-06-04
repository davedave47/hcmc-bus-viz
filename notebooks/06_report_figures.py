#!/usr/bin/env python3
"""06_report_figures.py — Static figures for the report.

Generates pedagogical and data figures referenced by the report's LaTeX
chapters. Idempotent: rerunning writes byte-identical PNGs against
fixed inputs (no random sampling, fixed colour palette, fixed seed).

Outputs to report/images/diagrams/, alongside the placeholder paths
declared in Appendix C of the report.

Current figures:
- solution_reject_pie_vs_bar.png  — Ch 4.7, why the pie is poor vs.
  the ranked bar on a five-category fare-class composition.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

ROOT = Path("/home/duyhuynh/Desktop/capstone")
OUT = ROOT / "report" / "images" / "diagrams"
OUT.mkdir(parents=True, exist_ok=True)
PARQUET = ROOT / "data" / "parquet"


# -----------------------------------------------------------------
# Figure 1 — Pie vs. ranked bar on fare-class composition
# -----------------------------------------------------------------
def fig_reject_pie_vs_bar() -> Path:
    """Side-by-side comparison of pie and ranked horizontal bar on the
    same five-category fare-class composition.

    Pedagogical purpose: show that the pie obscures the rank order of
    the medium-sized slices (PT single 37 % vs. HS-SV single 21 % vs.
    PT multi-route 20 %), while the ranked bar surfaces the order
    immediately. Same data, same colour palette, different encoding.
    """
    categories = [
        "PT single (regular cash)",
        "HS-SV single (student cash)",
        "PT multi-route",
        "HS-SV multi-route",
        "Free-fare",
    ]
    shares = [37, 21, 20, 13, 9]  # sum = 100

    # Soft, muted palette. Same colour per category in both panels so
    # the only thing that changes across the two charts is the
    # primitive (angle/area vs. length).
    palette = {
        "PT single (regular cash)":     "#6B9AC4",  # blue
        "HS-SV single (student cash)":  "#D68A6E",  # burnt orange
        "PT multi-route":               "#93A3B8",  # cool grey
        "HS-SV multi-route":            "#C9A85F",  # muted gold
        "Free-fare":                    "#84A884",  # sage green
    }
    colors = [palette[c] for c in categories]

    # Sorted (descending) for the bar
    order = sorted(range(len(shares)), key=lambda i: -shares[i])
    bar_cats   = [categories[i] for i in order]
    bar_shares = [shares[i] for i in order]
    bar_colors = [palette[c] for c in bar_cats]

    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(12, 4.8), dpi=150)
    fig.patch.set_facecolor("white")

    # ---- Left: pie chart ----
    wedges, texts, autotexts = ax_l.pie(
        shares,
        labels=categories,
        colors=colors,
        autopct=lambda p: f"{int(round(p))}%",
        startangle=90,
        counterclock=False,
        textprops={"fontsize": 8.5, "color": "#1B2333"},
        wedgeprops={"linewidth": 1.8, "edgecolor": "white"},
        pctdistance=0.72,
    )
    for at in autotexts:
        at.set_fontsize(9)
        at.set_fontweight("bold")
        at.set_color("white")
    ax_l.set_title(
        "Pie chart:\nthe rank order of the medium slices is ambiguous.",
        fontsize=10.5, fontweight="600", color="#3A4256",
        pad=14, loc="left", x=-0.05, y=1.04,
    )

    # ---- Right: ranked horizontal bar ----
    y = np.arange(len(bar_cats))
    ax_r.barh(
        y, bar_shares,
        color=bar_colors,
        edgecolor="white", linewidth=0.8,
        height=0.72,
    )
    ax_r.set_yticks(y)
    ax_r.set_yticklabels(bar_cats, fontsize=9, color="#1B2333")
    ax_r.invert_yaxis()
    ax_r.set_xlim(0, 44)
    ax_r.set_xlabel("Share of boardings (%)", fontsize=9, color="#566070")
    ax_r.tick_params(axis="x", labelsize=8.5, colors="#566070")
    ax_r.tick_params(axis="y", length=0)
    for s in ("top", "right"):
        ax_r.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax_r.spines[s].set_color("#CCD2D6")
        ax_r.spines[s].set_linewidth(0.8)
    ax_r.grid(axis="x", color="#E5E8EA", linewidth=0.6, alpha=0.7)
    ax_r.set_axisbelow(True)

    # In-bar value labels
    for i, v in enumerate(bar_shares):
        ax_r.text(
            v + 0.6, i, f"{v}%",
            va="center", ha="left",
            fontsize=9, fontweight="600", color="#1B2333",
        )
    ax_r.set_title(
        "Ranked bar:\nrank order is immediate; magnitudes are comparable.",
        fontsize=10.5, fontweight="600", color="#3A4256",
        pad=14, loc="left", x=-0.02, y=1.04,
    )

    # Overall finding (Knaflic action title)
    fig.suptitle(
        "Same data, two primitives. The bar makes rank immediate; "
        "the pie ambiguates the order of medium-sized slices.",
        fontsize=12, fontweight="700", color="#1B2333",
        x=0.04, y=1.005, ha="left",
    )

    # Source footer
    fig.text(
        0.04, -0.025,
        "Source: AFC fare-class breakdown, Jan to Mar 2026 (illustrative shares; sum = 100%).",
        fontsize=8, color="#6E7689", ha="left", style="italic",
    )

    plt.tight_layout(rect=[0, 0, 1, 0.92])
    out = OUT / "solution_reject_pie_vs_bar.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white", pad_inches=0.3)
    plt.close(fig)
    return out


# -----------------------------------------------------------------
# Figure 2 — Tết shock case-study (Ch 1.1 motivation hero)
# -----------------------------------------------------------------
def fig_tet_shock() -> Path:
    """Daily AFC boardings across the 90-day window with the Tết
    holiday window annotated.

    Pedagogical purpose: anchor the motivation in a real, dated finding
    drawn from the project's own data. The chart follows the Knaflic
    action-title-plus-subtitle invariant from §3.5 of the report.
    """
    # Tickets are stored as 90 daily parquet files under tickets/.
    files = sorted((PARQUET / "tickets").glob("*.parquet"))
    if not files:
        raise RuntimeError(
            f"No ticket parquet files found under {PARQUET / 'tickets'}"
        )
    # time_created_ticket is a unix timestamp in milliseconds.
    parts = []
    for f in files:
        df = pl.read_parquet(f, columns=["time_created_ticket"])
        parts.append(df)
    tickets = pl.concat(parts)
    daily = (
        tickets
        .with_columns(
            pl.from_epoch(pl.col("time_created_ticket"), time_unit="s")
            .cast(pl.Date)
            .alias("d")
        )
        .group_by("d")
        .agg(pl.len().alias("n"))
        .sort("d")
    )
    # Convert to Python lists for matplotlib.
    dates = daily["d"].to_list()
    counts = daily["n"].to_list()

    # Identify Tết minimum date and value for annotation.
    # Tết Nguyên Đán 2026 is 17 February (Year of the Horse); the
    # public-holiday window runs roughly 14-22 February.
    import datetime as _dt
    tet_start = _dt.date(2026, 2, 14)
    tet_end   = _dt.date(2026, 2, 22)
    recovery  = _dt.date(2026, 2, 25)
    pre_window = [c for d, c in zip(dates, counts)
                  if _dt.date(2026, 1, 8) <= d <= _dt.date(2026, 2, 10)]
    baseline = float(np.median(pre_window)) if pre_window else max(counts)
    in_tet = [(d, c) for d, c in zip(dates, counts) if tet_start <= d <= tet_end]
    if in_tet:
        min_d, min_c = min(in_tet, key=lambda x: x[1])
    else:
        min_d, min_c = dates[len(dates)//2], min(counts)
    drop_pct = (1 - min_c / baseline) * 100 if baseline > 0 else 0.0

    fig, ax = plt.subplots(figsize=(11.5, 4.2), dpi=150)
    fig.patch.set_facecolor("white")

    # Tết window shading
    ax.axvspan(tet_start, tet_end, color="#F2C57C", alpha=0.35, zorder=1)
    # Pre-Tết baseline line
    ax.axhline(baseline, color="#93A3B8", linestyle="--", linewidth=0.9,
               zorder=2)

    # Main daily line
    ax.plot(dates, counts, color="#1E5F8E", linewidth=1.5,
            marker="o", markersize=2.4, markerfacecolor="#1E5F8E",
            markeredgewidth=0, zorder=3)

    # Highlight Tết minimum
    ax.scatter([min_d], [min_c], color="#C0392B", s=70, zorder=5,
               edgecolor="white", linewidth=1.0)
    ax.annotate(
        f"  Tết trough: {min_d:%d %b}\n  ({drop_pct:.0f} % below baseline)",
        xy=(min_d, min_c),
        xytext=(20, 28),
        textcoords="offset points",
        fontsize=9.5, color="#1B2333", fontweight="600",
        arrowprops=dict(arrowstyle="-", color="#C0392B", linewidth=0.7),
    )
    # Baseline label
    ax.text(dates[2], baseline * 1.04,
            f"Jan baseline ≈ {baseline/1000:.0f}k boardings/day",
            fontsize=8.5, color="#566070", style="italic")
    # Recovery marker
    ax.axvline(recovery, color="#5C8A5C", linestyle=":", linewidth=0.9, zorder=2)
    ax.text(recovery, max(counts) * 0.98,
            f"  recovery\n  ({recovery:%d %b})",
            fontsize=8.5, color="#3E6B3E", ha="left", va="top")

    # Knaflic action title + supporting subtitle
    fig.text(0.07, 0.965,
             f"Tết drops daily ridership by {drop_pct:.0f} % for nine days, then recovers by 12 February.",
             fontsize=12.5, fontweight="700", color="#1B2333", ha="left")
    fig.text(0.07, 0.925,
             "Daily AFC boardings, HCMC bus network, 1 January to 31 March 2026.",
             fontsize=9.5, color="#566070", ha="left", style="italic")

    # Axis cosmetics
    ax.set_ylabel("Boardings per day", fontsize=9.5, color="#566070")
    ax.tick_params(axis="both", labelsize=8.5, colors="#566070")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#CCD2D6")
        ax.spines[s].set_linewidth(0.8)
    ax.grid(axis="y", color="#E5E8EA", linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)

    # Date formatting
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO,
                                                     interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    fig.autofmt_xdate(rotation=0, ha="center")

    # Footer
    fig.text(0.07, 0.02,
             "Source: AFC tickets.parquet, 90-day window (project own data).",
             fontsize=8, color="#6E7689", ha="left", style="italic")

    plt.subplots_adjust(left=0.07, right=0.97, top=0.86, bottom=0.13)
    out = OUT / "intro_tet_shock.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white",
                pad_inches=0.2)
    plt.close(fig)
    return out


# -----------------------------------------------------------------
# Figure 3 — Before/after declutter (Ch 3.5 storytelling)
# -----------------------------------------------------------------
def fig_declutter() -> Path:
    """Two panels showing the same monthly-ridership data: a cluttered
    version (rainbow colours, full grid, legend, distracting marks)
    and a decluttered version (single accent, minimal grid, direct
    annotation). Demonstrates the focus-attention principle from
    Knaflic.
    """
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    series_a = [82, 78, 88, 85, 92, 95, 94, 96, 98, 102, 105, 110]
    series_b = [70, 68, 72, 74, 79, 81, 80, 82, 85, 88, 90, 92]
    series_c = [55, 60, 58, 65, 64, 69, 71, 73, 75, 76, 78, 80]

    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(11, 4.0), dpi=150)
    fig.patch.set_facecolor("white")

    # -------- left panel: cluttered --------
    rainbow = ["#E63946", "#F1A208", "#2A9D8F"]
    ax_l.plot(months, series_a, "-o", color=rainbow[0], linewidth=2.4,
              markersize=7, label="Route A")
    ax_l.plot(months, series_b, "-s", color=rainbow[1], linewidth=2.4,
              markersize=7, label="Route B")
    ax_l.plot(months, series_c, "-^", color=rainbow[2], linewidth=2.4,
              markersize=7, label="Route C")
    ax_l.set_facecolor("#F5F5F0")
    ax_l.grid(True, which="both", color="#888888", linewidth=0.6, alpha=0.7)
    ax_l.minorticks_on()
    ax_l.grid(which="minor", color="#BBBBBB", linewidth=0.4, alpha=0.5)
    ax_l.set_xlabel("Month of year", fontsize=10, fontweight="bold")
    ax_l.set_ylabel("Monthly boardings (thousands)", fontsize=10,
                    fontweight="bold")
    ax_l.set_title("Monthly boardings by route", fontsize=11,
                   fontweight="bold")
    ax_l.legend(loc="upper left", fontsize=9, frameon=True,
                fancybox=True, shadow=True)
    for spine in ax_l.spines.values():
        spine.set_color("#444444")
        spine.set_linewidth(1.2)
    ax_l.tick_params(axis="both", which="both", labelsize=9)

    # -------- right panel: decluttered --------
    muted_grey = "#B8BEC7"
    accent = "#1E5F8E"
    ax_r.plot(months, series_b, "-", color=muted_grey, linewidth=1.4)
    ax_r.plot(months, series_c, "-", color=muted_grey, linewidth=1.4)
    ax_r.plot(months, series_a, "-", color=accent, linewidth=2.6)
    # direct labels at the right edge
    ax_r.text(11.15, series_a[-1], "Route A",
              color=accent, fontsize=9.5, fontweight="600", va="center")
    ax_r.text(11.15, series_b[-1], "Route B",
              color="#7E8593", fontsize=9, va="center")
    ax_r.text(11.15, series_c[-1], "Route C",
              color="#7E8593", fontsize=9, va="center")
    # action-title-style finding above
    ax_r.annotate(
        "Route A grows 34% across the year",
        xy=(11, series_a[-1]), xytext=(2.5, 115),
        fontsize=10.5, fontweight="700", color="#1B2333",
        arrowprops=dict(arrowstyle="->", color=accent, linewidth=0.8,
                        connectionstyle="arc3,rad=-0.15"),
    )
    for s in ("top", "right"):
        ax_r.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax_r.spines[s].set_color("#CCD2D6")
        ax_r.spines[s].set_linewidth(0.7)
    ax_r.tick_params(axis="both", labelsize=8.5, colors="#566070",
                     length=2)
    ax_r.set_ylim(40, 130)
    ax_r.set_xlim(-0.3, 12.5)
    # one subtle horizontal guide
    ax_r.grid(axis="y", color="#E5E8EA", linewidth=0.5, alpha=0.6)
    ax_r.set_axisbelow(True)

    # subtitles
    ax_l.text(0.02, 1.18, "Cluttered version",
              transform=ax_l.transAxes,
              fontsize=11, fontweight="700", color="#1B2333")
    ax_r.text(0.02, 1.18, "Decluttered version",
              transform=ax_r.transAxes,
              fontsize=11, fontweight="700", color="#1B2333")

    plt.subplots_adjust(left=0.07, right=0.95, top=0.84, bottom=0.13,
                        wspace=0.32)
    out = OUT / "foundations_declutter.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white",
                pad_inches=0.25)
    plt.close(fig)
    return out


# -----------------------------------------------------------------
# Main
# -----------------------------------------------------------------
if __name__ == "__main__":
    figures = [
        ("fig_reject_pie_vs_bar", fig_reject_pie_vs_bar),
        ("fig_tet_shock",         fig_tet_shock),
        ("fig_declutter",         fig_declutter),
    ]
    print("=" * 60)
    print("Generating report figures")
    print("=" * 60)
    for name, fn in figures:
        path = fn()
        size_kb = path.stat().st_size / 1024
        print(f"  ✓ {name:<32} {path.name:<48} ({size_kb:.1f} KB)")
    print("Done.")
