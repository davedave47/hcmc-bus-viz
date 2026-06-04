#!/usr/bin/env python3
"""05_programmatic_eda.py — fresh, systematic profile of every raw CSV.

Runs the /programmatic-eda + /schema-mapper skills end-to-end with NO solution
context: it discovers every file under data/raw, describes its shape and
quality, and reports what joins what. Outputs are idempotent.

Outputs:
  report/images/figures/eda_*.png  — generated plots
  notebooks/05_eda_report.md       — per-table profile (full)
  notebooks/05_findings.md         — top quality issues + recommendations
  notebooks/05_schema_map.md       — column overlap + join-key candidates
  notebooks/05_profiles.json       — machine-readable profile per table
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import seaborn as sns

# ---------- paths ----------
ROOT = Path("/home/duyhuynh/Desktop/capstone")
RAW = ROOT / "data" / "raw"
FIG = ROOT / "report" / "images" / "figures"
OUT = ROOT / "notebooks"
FIG.mkdir(exist_ok=True, parents=True)

sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams.update({"figure.dpi": 110, "savefig.bbox": "tight"})

# Thresholds (from skill references/quality_thresholds.md)
NULL_WARN, NULL_FAIL = 30.0, 70.0
DUP_WARN = 1.0
HCM_LAT, HCM_LNG = (10.0, 11.5), (106.0, 107.5)

# =============================================================
# 1. INVENTORY
# =============================================================
def inventory() -> dict:
    """Return logical_name -> dict(paths, source, kind)."""
    t = {}
    for p in sorted(RAW.glob("*.csv")):
        t[f"root.{p.stem}"] = {"paths": [p], "source": "root", "kind": "single"}
    for p in sorted((RAW / "gps").glob("*.csv")):
        t[f"gps.{p.stem}"] = {"paths": [p], "source": "gps", "kind": "single"}
    raw_gps = sorted((RAW / "gps" / "raw_gps").glob("*.csv"))
    if raw_gps:
        t["gps.raw_pings"] = {"paths": raw_gps, "source": "gps", "kind": "daily"}
    ext = sorted((RAW / "gps" / "extracted_trips_buffer_50m").rglob("*.csv"))
    if ext:
        t["gps.extracted_trips"] = {"paths": ext, "source": "gps", "kind": "per_entity"}
    for p in sorted((RAW / "tickets").glob("*.csv")):
        t[f"afc.{p.stem}"] = {"paths": [p], "source": "afc", "kind": "single"}
    trips = sorted((RAW / "tickets").glob("*_2026/trips.csv"))
    if trips:
        t["afc.trips"] = {"paths": trips, "source": "afc", "kind": "monthly"}
    tk = sorted((RAW / "tickets").rglob("tickets/*.csv"))
    if tk:
        t["afc.tickets"] = {"paths": tk, "source": "afc", "kind": "daily"}
    pay = sorted((RAW / "tickets").rglob("payments/*.csv"))
    if pay:
        t["afc.payments"] = {"paths": pay, "source": "afc", "kind": "daily"}
    return t


# =============================================================
# 2. LOAD & PROFILE
# =============================================================
def _safe_read(p: Path) -> pl.DataFrame | None:
    try:
        return pl.read_csv(p, infer_schema_length=20000, ignore_errors=True,
                           null_values=["", "NA", "null", "NULL"])
    except Exception as e:
        print(f"    WARN read fail {p.name}: {e}")
        return None


def load_logical(spec: dict, big_threshold_mb: float = 250) -> tuple[pl.DataFrame | None, str]:
    """Load one logical table. For big multi-file tables, sample."""
    paths = spec["paths"]
    total_mb = sum(p.stat().st_size for p in paths) / 1e6
    note = ""
    if len(paths) == 1:
        return _safe_read(paths[0]), note
    # sampling rules for multi-file
    if spec["kind"] == "per_entity" and len(paths) > 40:
        sample = paths[:30]
        note = f"sampled 30 of {len(paths):,} per-trip files"
    elif spec["kind"] == "daily" and total_mb > big_threshold_mb:
        by_root = defaultdict(list)
        for p in paths:
            by_root[p.parent.parent.name].append(p)
        sample = [v[len(v) // 2] for v in by_root.values()]
        note = f"sampled 1 day per month ({len(sample)} of {len(paths)} files)"
    else:
        sample = paths
        note = f"loaded all {len(paths)} files"
    dfs = [_safe_read(p) for p in sample]
    dfs = [d for d in dfs if d is not None]
    if not dfs:
        return None, note
    return pl.concat(dfs, how="diagonal_relaxed"), note


def profile_one(name: str, spec: dict) -> tuple[dict, pl.DataFrame | None]:
    paths = spec["paths"]
    size_mb = round(sum(p.stat().st_size for p in paths) / 1e6, 2)
    df, note = load_logical(spec)
    base = {
        "source": spec["source"],
        "kind": spec["kind"],
        "n_files": len(paths),
        "size_mb_total": size_mb,
        "sample_note": note,
    }
    if df is None or df.height == 0:
        base["error"] = "no data loaded"
        return base, None
    rows, cols = df.height, df.width
    prof = {
        **base,
        "rows_profiled": rows,
        "cols": cols,
        "columns": df.columns,
        "dtypes": {c: str(df.schema[c]) for c in df.columns},
        "null_pct": {c: round(100 * df[c].null_count() / rows, 2) for c in df.columns},
        "cardinality": {c: int(df[c].n_unique()) for c in df.columns},
    }
    prof["pk_candidates"] = [
        c for c in df.columns
        if prof["cardinality"][c] == rows and prof["null_pct"][c] == 0
    ]
    ns = {}
    for c in df.columns:
        if df.schema[c].is_numeric():
            s = df[c].drop_nulls()
            if len(s):
                try:
                    ns[c] = {
                        "min": float(s.min()), "max": float(s.max()),
                        "mean": float(s.mean()), "median": float(s.median()),
                        "std": float(s.std()) if len(s) > 1 else 0.0,
                        "p5": float(s.quantile(0.05)), "p95": float(s.quantile(0.95)),
                    }
                except Exception:
                    pass
    prof["numeric_stats"] = ns
    cats = {}
    for c in df.columns:
        if df.schema[c] == pl.Utf8 and prof["cardinality"][c] <= 50:
            try:
                vc = df[c].value_counts().sort("count", descending=True).head(3)
                cats[c] = vc.to_dicts()
            except Exception:
                pass
    prof["top_categories"] = cats
    return prof, df


# =============================================================
# 3. VALIDITY CHECKS
# =============================================================
def validity(profiles: dict, dfs: dict) -> list[dict]:
    issues = []
    for name, prof in profiles.items():
        if "error" in prof:
            issues.append({"severity": "ERROR", "table": name, "issue": prof["error"]})
            continue
        for c, p in prof.get("null_pct", {}).items():
            if p == 100:
                issues.append({"severity": "FAIL", "table": name, "issue": f"`{c}` 100% null"})
            elif p >= NULL_FAIL:
                issues.append({"severity": "FAIL", "table": name, "issue": f"`{c}` {p}% null"})
            elif p >= NULL_WARN:
                issues.append({"severity": "WARN", "table": name, "issue": f"`{c}` {p}% null"})
        df = dfs.get(name)
        if df is None:
            continue
        lat_col = next((c for c in df.columns if c.lower() in ("lat", "latitude")), None)
        lng_col = next((c for c in df.columns if c.lower() in ("lng", "lon", "long", "longitude")), None)
        if lat_col and lng_col:
            try:
                la = df[lat_col].drop_nulls()
                lo = df[lng_col].drop_nulls()
                if la.dtype.is_numeric() and lo.dtype.is_numeric():
                    bad_la = int(((la < HCM_LAT[0]) | (la > HCM_LAT[1])).sum())
                    bad_lo = int(((lo < HCM_LNG[0]) | (lo > HCM_LNG[1])).sum())
                    if bad_la:
                        issues.append({"severity": "WARN", "table": name,
                                       "issue": f"{bad_la:,} `{lat_col}` outside HCMC bbox [{HCM_LAT[0]}, {HCM_LAT[1]}]"})
                    if bad_lo:
                        issues.append({"severity": "WARN", "table": name,
                                       "issue": f"{bad_lo:,} `{lng_col}` outside HCMC bbox [{HCM_LNG[0]}, {HCM_LNG[1]}]"})
            except Exception:
                pass
        if "speed" in df.columns and df.schema["speed"].is_numeric():
            s = df["speed"].drop_nulls()
            if len(s):
                bad = int(((s < 0) | (s > 120)).sum())
                if bad:
                    issues.append({"severity": "WARN", "table": name,
                                   "issue": f"`speed` {bad:,} values outside [0, 120] km/h"})
        if not prof.get("pk_candidates"):
            try:
                dup = df.height - df.unique().height
                if dup > 0:
                    rate = round(100 * dup / df.height, 2)
                    if rate >= DUP_WARN:
                        issues.append({"severity": "WARN", "table": name,
                                       "issue": f"{dup:,} ({rate}%) full-row duplicates, no PK detected"})
            except Exception:
                pass
    return issues


# =============================================================
# 4. SCHEMA DISCOVERY
# =============================================================
def shared_columns(profiles: dict) -> dict:
    m = defaultdict(list)
    for n, p in profiles.items():
        if "columns" in p:
            for c in p["columns"]:
                m[c].append(n)
    return {c: ts for c, ts in m.items() if len(ts) >= 2}


def joinability_pct(df_a, df_b, col):
    try:
        a = set(df_a[col].drop_nulls().to_list())
        b = set(df_b[col].drop_nulls().to_list())
        if not a or not b:
            return None
        inter = a & b
        return {
            "a_uniq": len(a), "b_uniq": len(b), "shared": len(inter),
            "a_in_b": round(100 * len(inter) / len(a), 2),
            "b_in_a": round(100 * len(inter) / len(b), 2),
        }
    except Exception:
        return None


# =============================================================
# 5. FIGURES
# =============================================================
SOURCE_COLOR = {"root": "#6b7280", "gps": "#2563eb", "afc": "#16a34a"}

def fig_inventory(profiles: dict):
    rows = []
    for n, p in profiles.items():
        if "rows_profiled" not in p:
            continue
        rows.append((n, p["source"], p["rows_profiled"], p["size_mb_total"]))
    rows.sort(key=lambda r: r[2])
    names = [r[0] for r in rows]
    counts = [r[2] for r in rows]
    colors = [SOURCE_COLOR[r[1]] for r in rows]
    fig, ax = plt.subplots(figsize=(9, 0.32 * len(rows) + 1.5))
    ax.barh(names, counts, color=colors)
    ax.set_xscale("log")
    ax.set_xlabel("rows profiled (log scale)")
    ax.set_title("EDA Inventory — every raw table, by row count")
    for i, (n, src, r, mb) in enumerate(rows):
        ax.text(r * 1.05, i, f" {r:,}  ·  {mb} MB", va="center", fontsize=8)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=v, label=k) for k, v in SOURCE_COLOR.items()],
              loc="lower right", title="source")
    fig.savefig(FIG / "eda_inventory.png")
    plt.close(fig)


def fig_nulls_heatmap(profiles: dict, source: str):
    rows = [(n, p) for n, p in profiles.items()
            if p.get("source") == source and "null_pct" in p]
    if not rows:
        return
    all_cols = sorted({c for _, p in rows for c in p["null_pct"]})
    M = np.full((len(rows), len(all_cols)), np.nan)
    for i, (_, p) in enumerate(rows):
        for j, c in enumerate(all_cols):
            if c in p["null_pct"]:
                M[i, j] = p["null_pct"][c]
    fig, ax = plt.subplots(figsize=(max(8, 0.35 * len(all_cols)),
                                    max(3, 0.4 * len(rows))))
    sns.heatmap(M, ax=ax, cmap="Reds", vmin=0, vmax=100, cbar_kws={"label": "% null"},
                xticklabels=all_cols, yticklabels=[r[0] for r in rows],
                mask=np.isnan(M), linewidths=0.4, linecolor="white")
    ax.set_title(f"Null % heatmap — {source.upper()} tables")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=60, ha="right", fontsize=8)
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=8)
    fig.savefig(FIG / f"eda_nulls_{source}.png")
    plt.close(fig)


def fig_dtype_distribution(profiles: dict):
    rows = []
    for n, p in profiles.items():
        if "dtypes" not in p:
            continue
        counts = defaultdict(int)
        for dt in p["dtypes"].values():
            base = dt.split("(")[0].rstrip(")")
            counts[base] += 1
        for dt, c in counts.items():
            rows.append({"table": n, "dtype": dt, "count": c, "source": p["source"]})
    if not rows:
        return
    import pandas as pd
    df = pd.DataFrame(rows)
    pivot = df.pivot_table(index="table", columns="dtype", values="count",
                           aggfunc="sum", fill_value=0)
    fig, ax = plt.subplots(figsize=(9, 0.32 * len(pivot) + 1.5))
    pivot.plot.barh(stacked=True, ax=ax, cmap="tab20", width=0.8)
    ax.set_title("Column dtype composition per table")
    ax.set_xlabel("# columns")
    ax.legend(title="dtype", loc="lower right", fontsize=7, ncol=2)
    fig.savefig(FIG / "eda_dtypes.png")
    plt.close(fig)


def fig_speed_distribution(dfs: dict):
    for name, df in dfs.items():
        if "speed" not in df.columns or not df.schema["speed"].is_numeric():
            continue
        s = df["speed"].drop_nulls().to_numpy()
        if len(s) == 0:
            continue
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.hist(s, bins=80, color="#2563eb", alpha=0.85)
        ax.axvline(0, color="red", linestyle="--", linewidth=1, label="0 km/h")
        ax.axvline(120, color="red", linestyle="--", linewidth=1, label="120 km/h (plausible cap)")
        ax.set_xlabel("speed (km/h)")
        ax.set_ylabel("count")
        ax.set_title(f"Speed distribution — {name}")
        ax.legend()
        med = float(np.median(s))
        ax.text(0.98, 0.95, f"n = {len(s):,}\nmedian = {med:.1f}\nmax = {s.max():.1f}",
                transform=ax.transAxes, ha="right", va="top",
                bbox=dict(facecolor="white", alpha=0.8, edgecolor="none"))
        fig.savefig(FIG / f"eda_speed_{name.replace('.', '_')}.png")
        plt.close(fig)


def fig_coord_validity(dfs: dict):
    fig, ax = plt.subplots(figsize=(7, 7))
    for name, df in dfs.items():
        cols = df.columns
        lat_col = next((c for c in cols if c.lower() in ("lat", "latitude")), None)
        lng_col = next((c for c in cols if c.lower() in ("lng", "lon", "long", "longitude")), None)
        if not (lat_col and lng_col):
            continue
        if not (df.schema[lat_col].is_numeric() and df.schema[lng_col].is_numeric()):
            continue
        sub = df.select([lat_col, lng_col]).drop_nulls()
        if sub.height == 0:
            continue
        n = min(5000, sub.height)
        sub = sub.sample(n, seed=42) if sub.height > n else sub
        la = sub[lat_col].to_numpy()
        lo = sub[lng_col].to_numpy()
        src = name.split(".")[0]
        ax.scatter(lo, la, s=4, alpha=0.4, color=SOURCE_COLOR.get(src, "#999"),
                   label=f"{name} (n={n})")
    # HCMC bbox
    ax.add_patch(plt.Rectangle((HCM_LNG[0], HCM_LAT[0]),
                               HCM_LNG[1] - HCM_LNG[0], HCM_LAT[1] - HCM_LAT[0],
                               fill=False, edgecolor="red", linewidth=1.5,
                               linestyle="--", label="HCMC bbox"))
    ax.set_xlabel("longitude")
    ax.set_ylabel("latitude")
    ax.set_title("Coordinate validity — all tables with lat/lng")
    ax.legend(fontsize=8, markerscale=2)
    fig.savefig(FIG / "eda_coord_validity.png")
    plt.close(fig)


def fig_cardinality(profiles: dict):
    pts = []
    for n, p in profiles.items():
        if "cardinality" not in p:
            continue
        rows = p.get("rows_profiled", 1)
        for c, k in p["cardinality"].items():
            pts.append({"table": n, "col": c, "card": k, "rows": rows,
                        "ratio": k / max(rows, 1)})
    if not pts:
        return
    import pandas as pd
    df = pd.DataFrame(pts)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(df["rows"], df["card"], s=20, alpha=0.5, c="#2563eb")
    ax.plot([1, df["rows"].max()], [1, df["rows"].max()],
            "k--", linewidth=0.7, label="cardinality = rows (PK)")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("rows in table (log)")
    ax.set_ylabel("unique values in column (log)")
    ax.set_title("Cardinality vs row count — high points are likely keys")
    ax.legend()
    fig.savefig(FIG / "eda_cardinality.png")
    plt.close(fig)


def fig_join_overlap(joins: list[dict]):
    if not joins:
        return
    joins = sorted(joins, key=lambda j: -j["shared"])[:25]
    labels = [f"{j['col']}: {j['a']} ↔ {j['b']}" for j in joins]
    a_in_b = [j["a_in_b"] for j in joins]
    b_in_a = [j["b_in_a"] for j in joins]
    fig, ax = plt.subplots(figsize=(9, 0.42 * len(labels) + 1.2))
    y = np.arange(len(labels))
    ax.barh(y - 0.2, a_in_b, height=0.4, label="% of A keys present in B", color="#2563eb")
    ax.barh(y + 0.2, b_in_a, height=0.4, label="% of B keys present in A", color="#16a34a")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlim(0, 105)
    ax.set_xlabel("% overlap on join column")
    ax.set_title("Top 25 cross-table joinabilities — directional overlap")
    ax.legend(loc="lower right")
    for i, j in enumerate(joins):
        ax.text(101, i, f"  n={j['shared']:,}", va="center", fontsize=7)
    fig.savefig(FIG / "eda_join_overlap.png")
    plt.close(fig)


# =============================================================
# 6. REPORTS
# =============================================================
def write_eda_report(profiles, issues, path: Path):
    lines = ["# 05 — Programmatic EDA Report",
             "",
             "*Auto-generated by `notebooks/05_programmatic_eda.py`.* "
             "Each table profiled in isolation — no solution-context filtering.",
             ""]
    by_source = defaultdict(list)
    for n, p in profiles.items():
        by_source[p.get("source", "?")].append((n, p))
    for src in sorted(by_source):
        lines.append(f"## Source: `{src}`\n")
        for name, p in sorted(by_source[src]):
            lines.append(f"### `{name}`")
            if "error" in p:
                lines.append(f"- **ERROR:** {p['error']}\n")
                continue
            lines.append(f"- files: **{p['n_files']}**, size: **{p['size_mb_total']} MB**, kind: `{p['kind']}`")
            if p.get("sample_note"):
                lines.append(f"- sampling: {p['sample_note']}")
            lines.append(f"- rows profiled: **{p['rows_profiled']:,}** · cols: **{p['cols']}**")
            if p.get("pk_candidates"):
                lines.append(f"- **PK candidates:** {', '.join(f'`{c}`' for c in p['pk_candidates'])}")
            lines.append("")
            lines.append("| column | dtype | null % | cardinality | sample stats |")
            lines.append("|---|---|---:|---:|---|")
            for c in p["columns"]:
                dt = p["dtypes"][c].split("(")[0]
                nu = p["null_pct"][c]
                ka = p["cardinality"][c]
                stats = ""
                if c in p.get("numeric_stats", {}):
                    s = p["numeric_stats"][c]
                    stats = f"min={s['min']:.2f} · p50={s['median']:.2f} · max={s['max']:.2f}"
                elif c in p.get("top_categories", {}):
                    tops = ", ".join(f"`{d[c]}`×{d['count']}" for d in p["top_categories"][c][:2])
                    stats = tops
                lines.append(f"| `{c}` | {dt} | {nu} | {ka:,} | {stats} |")
            lines.append("")
    lines.append("---")
    lines.append("## Validity issues (auto-detected)")
    lines.append("")
    by_sev = defaultdict(list)
    for i in issues:
        by_sev[i["severity"]].append(i)
    for sev in ["ERROR", "FAIL", "WARN"]:
        if sev not in by_sev:
            continue
        lines.append(f"### {sev} ({len(by_sev[sev])})")
        for i in by_sev[sev][:50]:
            lines.append(f"- **{i['table']}** — {i['issue']}")
        lines.append("")
    path.write_text("\n".join(lines))


def write_findings(profiles, issues, shared, joins, path: Path):
    n_tables = len([p for p in profiles.values() if "error" not in p])
    n_rows = sum(p.get("rows_profiled", 0) for p in profiles.values())
    n_fail = sum(1 for i in issues if i["severity"] == "FAIL")
    n_warn = sum(1 for i in issues if i["severity"] == "WARN")
    by_sev = defaultdict(list)
    for i in issues:
        by_sev[i["severity"]].append(i)
    lines = [
        "# 05 — Findings Summary",
        "",
        f"**Scope:** {n_tables} tables profiled, {n_rows:,} rows scanned in this pass.",
        f"**Validity issues:** {n_fail} FAIL · {n_warn} WARN.",
        "",
        "## Top quality issues",
        "",
    ]
    for sev in ["FAIL", "WARN"]:
        for i in by_sev[sev][:10]:
            lines.append(f"- **[{sev}]** `{i['table']}` — {i['issue']}")
    lines += ["", "## Cross-table observations", ""]
    lines.append(f"- **{len(shared)}** column names appear in ≥ 2 tables (potential join keys).")
    if joins:
        clean = [j for j in joins if j["a_in_b"] >= 80 or j["b_in_a"] >= 80]
        lines.append(f"- **{len(clean)}** of the {len(joins)} computed joins are ≥ 80% overlap in at least one direction (clean joins).")
        weak = [j for j in joins if j["a_in_b"] < 50 and j["b_in_a"] < 50]
        lines.append(f"- **{len(weak)}** joins are < 50% overlap both directions (lossy joins — likely different populations).")
    lines += ["", "## Recommendations", ""]
    recs = []
    if n_fail:
        recs.append("Address every **FAIL** issue (≥ 70% null or full-table-null columns) — these columns are either misnamed, sourced from a feature that isn't populated, or shouldn't be in the warehouse at all.")
    if n_warn:
        recs.append("Decide a policy for **WARN-level null columns** (30–70%) — drop, impute, or document as expected-sparse.")
    if any(i["issue"].startswith("speed") for i in issues):
        recs.append("Clip / flag GPS `speed` outliers above 120 km/h before computing aggregates — physically impossible on HCMC streets.")
    if any("bbox" in i["issue"] for i in issues):
        recs.append("Geocode-validate every coord column — even small fractions outside HCMC bbox imply ingestion bugs (swapped lat/lng, decimal-shift errors).")
    if joins and any(j["a_in_b"] < 50 and j["b_in_a"] < 50 for j in joins):
        recs.append("Document **lossy joins** explicitly in the warehouse spec — every aggregate built on them inherits the loss.")
    recs.append("Re-run this script (`python notebooks/05_programmatic_eda.py`) whenever raw data changes — it's idempotent and gives a baseline diff.")
    for r in recs:
        lines.append(f"- {r}")
    path.write_text("\n".join(lines))


def write_schema_map(profiles, shared, joins, path: Path):
    lines = ["# 05 — Schema Map", "",
             "*Cross-table column overlap + computed joinability. "
             "Inferred purely from column names + value overlap; no business rules applied.*",
             "",
             "## Shared column names (candidate join keys)",
             "",
             "| column | tables (count) | tables (list) |",
             "|---|---:|---|"]
    for c in sorted(shared, key=lambda c: -len(shared[c])):
        ts = shared[c]
        lines.append(f"| `{c}` | {len(ts)} | {', '.join(f'`{t}`' for t in sorted(ts))} |")
    lines += ["", "## Computed joinability (directional overlap %)",
              "",
              "| col | A | B | A unique | B unique | shared | A in B % | B in A % | interpretation |",
              "|---|---|---|---:|---:|---:|---:|---:|---|"]
    for j in sorted(joins, key=lambda x: -x["shared"]):
        a_in_b, b_in_a = j["a_in_b"], j["b_in_a"]
        if a_in_b >= 95 and b_in_a >= 95:
            interp = "**full overlap** — safe join"
        elif a_in_b >= 80 or b_in_a >= 80:
            interp = "high one-way overlap — child→parent join"
        elif a_in_b >= 30 or b_in_a >= 30:
            interp = "partial — populations differ"
        else:
            interp = "**lossy** — likely different keyspaces"
        lines.append(f"| `{j['col']}` | `{j['a']}` | `{j['b']}` | {j['a_uniq']:,} | {j['b_uniq']:,} | {j['shared']:,} | {a_in_b} | {b_in_a} | {interp} |")
    lines += ["", "## Per-table PK candidates", "",
              "| table | PK candidate(s) |", "|---|---|"]
    for n in sorted(profiles):
        p = profiles[n]
        pks = p.get("pk_candidates") or []
        lines.append(f"| `{n}` | {', '.join(f'`{c}`' for c in pks) if pks else '_(none — no unique 0-null column)_'} |")
    path.write_text("\n".join(lines))


# =============================================================
# 7. MAIN
# =============================================================
def main():
    print("=" * 72)
    print("STEP 1 — inventory")
    tables = inventory()
    print(f"  → {len(tables)} logical tables\n")

    print("STEP 2 — profile each table")
    profiles, dfs = {}, {}
    for name, spec in tables.items():
        p, df = profile_one(name, spec)
        profiles[name] = p
        if df is not None:
            dfs[name] = df
        rows = p.get("rows_profiled", "?")
        cols = p.get("cols", "?")
        print(f"  {name:<32}  {str(rows):>12}  ×  {cols}  cols")
    print()

    print("STEP 3 — validity checks")
    issues = validity(profiles, dfs)
    sev = defaultdict(int)
    for i in issues:
        sev[i["severity"]] += 1
    print(f"  → {dict(sev)}\n")

    print("STEP 4 — schema discovery")
    shared = shared_columns(profiles)
    print(f"  → {len(shared)} shared column names\n")

    print("STEP 5 — joinability (computed for every shared column across every pair)")
    joins = []
    for col, ts in shared.items():
        for i in range(len(ts)):
            for j in range(i + 1, len(ts)):
                a, b = ts[i], ts[j]
                if a in dfs and b in dfs:
                    r = joinability_pct(dfs[a], dfs[b], col)
                    if r and r["shared"] > 0:
                        joins.append({"col": col, "a": a, "b": b, **r})
    joins.sort(key=lambda x: -x["shared"])
    print(f"  → {len(joins)} non-empty joins computed\n")

    print("STEP 6 — generate figures")
    fig_inventory(profiles); print("  ✓ eda_inventory.png")
    for src in ("root", "gps", "afc"):
        fig_nulls_heatmap(profiles, src); print(f"  ✓ eda_nulls_{src}.png")
    fig_dtype_distribution(profiles); print("  ✓ eda_dtypes.png")
    fig_speed_distribution(dfs); print("  ✓ eda_speed_*.png")
    fig_coord_validity(dfs); print("  ✓ eda_coord_validity.png")
    fig_cardinality(profiles); print("  ✓ eda_cardinality.png")
    fig_join_overlap(joins); print("  ✓ eda_join_overlap.png\n")

    print("STEP 7 — write reports")
    write_eda_report(profiles, issues, OUT / "05_eda_report.md")
    print(f"  ✓ {OUT / '05_eda_report.md'}")
    write_findings(profiles, issues, shared, joins, OUT / "05_findings.md")
    print(f"  ✓ {OUT / '05_findings.md'}")
    write_schema_map(profiles, shared, joins, OUT / "05_schema_map.md")
    print(f"  ✓ {OUT / '05_schema_map.md'}")
    (OUT / "05_profiles.json").write_text(json.dumps(profiles, indent=2, default=str))
    print(f"  ✓ {OUT / '05_profiles.json'}")

    print("\nDONE.")


if __name__ == "__main__":
    main()
