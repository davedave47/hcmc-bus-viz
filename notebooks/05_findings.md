# 05 — Findings Summary

**Scope:** 24 tables profiled, 3,491,010 rows scanned in this pass.
**Validity issues:** 9 FAIL · 14 WARN.

## Top quality issues

- **[FAIL]** `root.hcmc_stops_agu_2025` — `support_disability` 80.36% null
- **[FAIL]** `afc.buses` — `category` 80.52% null
- **[FAIL]** `afc.trips` — `driver_license_number` 92.76% null
- **[FAIL]** `afc.tickets` — `user_id` 99.85% null
- **[FAIL]** `afc.tickets` — `user_id_duplicated_0` 99.85% null
- **[FAIL]** `afc.payments` — `promotion_code` 99.61% null
- **[FAIL]** `afc.payments` — `promotion_description` 99.61% null
- **[FAIL]** `afc.payments` — `emv_card_id` 98.93% null
- **[FAIL]** `afc.payments` — `verification_qr` 99.91% null
- **[WARN]** `root.hcmc_stops_agu_2025` — `ward` 52.21% null
- **[WARN]** `gps.drivers` — `driver_name` 58.67% null
- **[WARN]** `gps.routes` — 15 (8.15%) full-row duplicates, no PK detected
- **[WARN]** `gps.schedules` — `start_terminal_id` 54.22% null
- **[WARN]** `gps.schedules` — `end_terminal_id` 52.21% null
- **[WARN]** `gps.schedules` — 109,620 (38.72%) full-row duplicates, no PK detected
- **[WARN]** `gps.raw_pings` — `speed` 49.74% null
- **[WARN]** `afc.drivers` — 508 (43.31%) full-row duplicates, no PK detected
- **[WARN]** `afc.routes` — 15 (10.07%) full-row duplicates, no PK detected
- **[WARN]** `afc.stations` — 77 `lat` outside HCMC bbox [10.0, 11.5]

## Cross-table observations

- **32** column names appear in ≥ 2 tables (potential join keys).
- **58** of the 83 computed joins are ≥ 80% overlap in at least one direction (clean joins).
- **14** joins are < 50% overlap both directions (lossy joins — likely different populations).

## Recommendations

- Address every **FAIL** issue (≥ 70% null or full-table-null columns) — these columns are either misnamed, sourced from a feature that isn't populated, or shouldn't be in the warehouse at all.
- Decide a policy for **WARN-level null columns** (30–70%) — drop, impute, or document as expected-sparse.
- Geocode-validate every coord column — even small fractions outside HCMC bbox imply ingestion bugs (swapped lat/lng, decimal-shift errors).
- Document **lossy joins** explicitly in the warehouse spec — every aggregate built on them inherits the loss.
- Re-run this script (`python notebooks/05_programmatic_eda.py`) whenever raw data changes — it's idempotent and gives a baseline diff.