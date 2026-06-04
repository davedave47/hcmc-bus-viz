#!/usr/bin/env python3
"""07_eda_figures_live.py — regenerate the data-bearing EDA figures.

Reads the live warehouse (raw `tickets` + `payments`, the canonical
17,883,623-row Jan–Mar 2026 AFC window) and rewrites the five demand
figures + the six-tile headline figure with numbers that match the
warehouse. Replaces the stale figures generated from an earlier data
snapshot (which carried 34 % student, 9 % free, and a 26,419 Tết trough).

Idempotent: fixed palette, no sampling. Outputs:
  report/images/figures/eda_daily_boardings.png
  report/images/figures/eda_hourly_by_daytype.png
  report/images/figures/eda_fareclass_by_hour.png
  report/images/figures/eda_route_pareto.png
  report/images/figures/eda_payment_trend.png
  report/images/diagrams/eda_headlines.png
"""
from __future__ import annotations

from pathlib import Path

import duckdb
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

ROOT = Path("/home/duyhuynh/Desktop/capstone")
FIG = ROOT / "report" / "images" / "figures"
DIA = ROOT / "report" / "images" / "diagrams"
FIG.mkdir(parents=True, exist_ok=True)

INK, INK2, INK3 = "#1B2333", "#3A4256", "#6E7689"
ORANGE, GOLD, GREEN, RED, GREY = "#E45A2E", "#D9A12C", "#2F8A4F", "#C03A3A", "#C7CDD3"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.edgecolor": "#CCD2D6", "axes.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 13, "axes.titleweight": "bold", "axes.titlecolor": INK,
    "axes.labelcolor": INK2, "xtick.color": INK3, "ytick.color": INK3,
    "figure.facecolor": "white", "axes.facecolor": "white",
})

con = duckdb.connect(str(ROOT / "db" / "bus.duckdb"), read_only=True)


def _save(fig, path):
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white", pad_inches=0.25)
    plt.close(fig)
    print(f"  wrote {path.relative_to(ROOT)}")


def _tet_trough_drop(rows):
    """Trough drop % against the pre-Tết baseline (Jan 8 – Feb 7), the same
    window the product's dim_date marks as is_pre_tet_baseline. Returns
    (trough_date, trough_val, drop_pct)."""
    import datetime as _dt
    base = [n for d, n in rows if _dt.date(2026, 1, 8) <= d <= _dt.date(2026, 2, 7)]
    base_mean = sum(base) / len(base) if base else 0
    trough = min(rows, key=lambda r: r[1])
    drop = 100 * (1 - trough[1] / base_mean) if base_mean else 0
    return trough[0], trough[1], drop


def fig_daily_boardings():
    rows = con.execute("""
        SELECT to_timestamp(time_created_ticket)::DATE AS d, COUNT(*) n
        FROM tickets GROUP BY d ORDER BY d
    """).fetchall()
    days = [r[0] for r in rows]; vals = [r[1] for r in rows]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axvspan(__import__("datetime").date(2026, 2, 14), __import__("datetime").date(2026, 2, 22),
               color=RED, alpha=0.07, lw=0)
    ax.plot(days, vals, color=ORANGE, lw=1.8)
    ax.fill_between(days, vals, color=ORANGE, alpha=0.10)
    t_day, t_val, t_drop = _tet_trough_drop(rows)
    ax.annotate(f"{t_day:%-d %b} trough\n{t_val:,} (−{t_drop:.0f}%)",
                xy=(t_day, t_val), xytext=(t_day, t_val + 90000),
                ha="center", fontsize=9, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=1))
    ax.set_title("Daily AFC boardings, 1 January – 31 March 2026")
    ax.set_ylabel("boardings per day")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v/1000:.0f}k"))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.margins(x=0.01)
    _save(fig, FIG / "eda_daily_boardings.png")
    print(f"  [daily] trough {t_day} = {t_val:,} (−{t_drop:.1f}%)")


def fig_hourly_by_daytype():
    rows = con.execute("""
        SELECT extract(hour FROM to_timestamp(time_created_ticket))::INT h,
               CASE WHEN extract(dow FROM to_timestamp(time_created_ticket)) IN (0,6)
                    THEN 'weekend' ELSE 'weekday' END dt,
               COUNT(*) n,
               COUNT(DISTINCT to_timestamp(time_created_ticket)::DATE) d
        FROM tickets GROUP BY h, dt ORDER BY h
    """).fetchall()
    wd = {h: n/d for h, dt, n, d in rows if dt == "weekday"}
    we = {h: n/d for h, dt, n, d in rows if dt == "weekend"}
    hrs = list(range(24))
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(hrs, [wd.get(h, 0) for h in hrs], color=ORANGE, lw=2, marker="o", ms=3, label="weekday")
    ax.plot(hrs, [we.get(h, 0) for h in hrs], color=INK3, lw=2, marker="o", ms=3, label="weekend")
    ax.set_title("Average hourly boardings, weekday vs weekend")
    ax.set_xlabel("hour of day"); ax.set_ylabel("avg boardings per hour")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v/1000:.0f}k"))
    ax.set_xticks(range(0, 24, 2))
    ax.legend(frameon=False)
    _save(fig, FIG / "eda_hourly_by_daytype.png")


def fig_fareclass_by_hour():
    rows = con.execute("""
        SELECT extract(hour FROM to_timestamp(time_created_ticket))::INT h,
               CASE WHEN ticket_type LIKE '%HS-SV%' THEN 'student'
                    WHEN ticket_type LIKE '%miễn phí%' THEN 'free'
                    WHEN ticket_type LIKE '%TM%' THEN 'cash'
                    ELSE 'other' END fc,
               COUNT(*) n
        FROM tickets GROUP BY h, fc
    """).fetchall()
    hrs = list(range(24))
    cats = ["cash", "student", "free", "other"]
    cols = {"cash": INK2, "student": ORANGE, "free": GREEN, "other": GREY}
    data = {c: [0]*24 for c in cats}
    for h, fc, n in rows:
        data[fc][h] = n
    fig, ax = plt.subplots(figsize=(10, 4))
    bottom = [0]*24
    for c in cats:
        ax.bar(hrs, data[c], bottom=bottom, color=cols[c], label=c, width=0.8)
        bottom = [b + v for b, v in zip(bottom, data[c])]
    ax.set_title("Hourly boarding composition by fare-class group")
    ax.set_xlabel("hour of day"); ax.set_ylabel("boardings")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v/1e6:.1f}M"))
    ax.set_xticks(range(0, 24, 2))
    ax.legend(frameon=False, ncol=4, loc="upper right")
    _save(fig, FIG / "eda_fareclass_by_hour.png")


def fig_route_pareto():
    rows = con.execute("""
        SELECT r.route_no, COUNT(*) n FROM tickets t
        JOIN ticket_trips tt ON tt.trip_id=t.trip_id
        JOIN ticket_routes r ON r.route_id=tt.route_id
        WHERE r.route_no IS NOT NULL GROUP BY r.route_no ORDER BY n DESC
    """).fetchall()
    tot = sum(n for _, n in rows)
    top = rows[:50]
    cum, cums = 0, []
    for _, n in rows:
        cum += n; cums.append(100*cum/tot)
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.bar(range(1, 51), [n for _, n in top], color=ORANGE, width=0.85)
    ax.set_title("Top 50 routes by boarding volume, with cumulative share")
    ax.set_xlabel("route rank"); ax.set_ylabel("boardings")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v/1000:.0f}k"))
    ax2 = ax.twinx()
    ax2.plot(range(1, len(cums)+1), cums, color=INK, lw=1.6)
    ax2.axhline(80, color=GREY, ls="--", lw=1)
    # mark 80% crossing
    k80 = next(i for i, c in enumerate(cums, 1) if c >= 80)
    ax2.annotate(f"80% at route {k80}", xy=(k80, 80), xytext=(k80+8, 62),
                 fontsize=9, color=INK2, arrowprops=dict(arrowstyle="->", color=INK3, lw=1))
    ax2.set_ylim(0, 105); ax2.set_ylabel("cumulative %"); ax2.spines["top"].set_visible(False)
    ax2.set_xlim(0.5, 50.5)
    _save(fig, FIG / "eda_route_pareto.png")


def fig_payment_trend():
    rows = con.execute("""
        SELECT p.month, t.day, t.cash, t.noncash FROM (
          SELECT to_timestamp(time_created_ticket)::DATE day,
                 ticket_id FROM tickets
        ) t0
        JOIN (
          SELECT ticket_id,
                 CASE WHEN payment_method = 'Tiền mặt' THEN 1 ELSE 0 END cash,
                 CASE WHEN payment_method = 'Tiền mặt' THEN 0 ELSE 1 END noncash,
                 month
          FROM payments
        ) p ON p.ticket_id = t0.ticket_id
        JOIN LATERAL (SELECT t0.day day, p.cash cash, p.noncash noncash) t ON TRUE
        LIMIT 0
    """).fetchall() if False else None
    # Simpler: aggregate by day via join
    rows = con.execute("""
        SELECT to_timestamp(t.time_created_ticket)::DATE d,
               SUM(CASE WHEN p.payment_method = 'Tiền mặt' THEN 1 ELSE 0 END) cash,
               SUM(CASE WHEN p.payment_method <> 'Tiền mặt' THEN 1 ELSE 0 END) noncash
        FROM tickets t JOIN payments p ON p.ticket_id = t.ticket_id
        GROUP BY d ORDER BY d
    """).fetchall()
    days = [r[0] for r in rows]
    cash = [r[1] for r in rows]; noncash = [r[2] for r in rows]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.stackplot(days, cash, noncash, colors=[INK2, ORANGE], labels=["cash (96.2%)", "non-cash"])
    ax.set_title("Daily boardings stacked by payment channel")
    ax.set_ylabel("boardings per day")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v/1000:.0f}k"))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.legend(frameon=False, loc="upper right"); ax.margins(x=0.01)
    _save(fig, FIG / "eda_payment_trend.png")


def fig_headlines():
    tot = con.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    rev = con.execute("SELECT SUM(amount_money) FROM payments").fetchone()[0]
    student = con.execute("SELECT 100.0*SUM(CASE WHEN ticket_type LIKE '%HS-SV%' THEN 1 ELSE 0 END)/COUNT(*) FROM tickets").fetchone()[0]
    cash = con.execute("SELECT 100.0*SUM(CASE WHEN payment_method='Tiền mặt' THEN 1 ELSE 0 END)/COUNT(*) FROM payments").fetchone()[0]
    n_routes = con.execute("SELECT COUNT(DISTINCT route_no) FROM ticket_routes").fetchone()[0]
    # Boardings per route (same join as the Pareto figure) so the headline,
    # the Pareto chart, and the prose all agree.
    rroute = con.execute("""
        SELECT r.route_no, COUNT(*) n FROM tickets t
        JOIN ticket_trips tt ON tt.trip_id=t.trip_id
        JOIN ticket_routes r ON r.route_id=tt.route_id
        WHERE r.route_no IS NOT NULL GROUP BY r.route_no ORDER BY n DESC
    """).fetchall()
    tot_r = sum(n for _, n in rroute) or 1
    cum, k80 = 0, len(rroute)
    for i, (_, n) in enumerate(rroute, start=1):
        cum += n
        if cum / tot_r >= 0.80:
            k80 = i
            break
    top10_share = 100 * sum(n for _, n in rroute[:10]) / tot_r
    daily = con.execute("""
        SELECT to_timestamp(time_created_ticket)::DATE AS d, COUNT(*) n
        FROM tickets GROUP BY d ORDER BY d
    """).fetchall()
    t_day, _tv, t_drop = _tet_trough_drop(daily)
    tiles = [
        (f"{tot/1e6:.1f}M", "AFC boardings\nJan–Mar 2026", ORANGE),
        (f"₫{rev/1e9:.1f}B", "fare revenue", GOLD),
        (f"{student:.0f}%", "student-fare share", GREEN),
        (f"{cash:.0f}%", "cash payments", INK2),
        (f"{k80} / {n_routes}", "routes for 80%\nof boardings", RED),
        (f"−{t_drop:.0f}%", f"Tết trough\n({t_day:%-d %b})", "#6A4DB0"),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(11, 5))
    for ax, (big, lbl, col) in zip(axes.flat, tiles):
        ax.axis("off")
        ax.text(0.5, 0.62, big, ha="center", va="center", fontsize=34, fontweight="bold", color=col)
        ax.text(0.5, 0.24, lbl, ha="center", va="center", fontsize=11, color=INK3)
    fig.suptitle("Six headline findings from the 90-day AFC exploratory analysis",
                 fontsize=13, fontweight="bold", color=INK, y=1.02)
    _save(fig, DIA / "eda_headlines.png")
    print(f"  [headlines] cash={cash:.1f}% k80={k80}/{n_routes} top10={top10_share:.1f}% trough=−{t_drop:.1f}%")


if __name__ == "__main__":
    print("Regenerating EDA figures from the live warehouse …")
    fig_daily_boardings()
    fig_hourly_by_daytype()
    fig_fareclass_by_hour()
    fig_route_pareto()
    fig_payment_trend()
    fig_headlines()
    con.close()
    print("Done.")
