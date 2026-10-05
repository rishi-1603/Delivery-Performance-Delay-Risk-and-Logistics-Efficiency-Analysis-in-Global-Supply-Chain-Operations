# Methodology

## 1. Analytical question

The official problem statement lists four gaps: (1) no clear on-time vs delayed
measurement, (2) no understanding of *why* shipments are delayed, (3) no
visibility into high-risk regions/markets/modes, (4) no diagnostics for
`late_delivery_risk`. Every analysis in this project maps to one of those four.

## 2. Grain decision (the most important call in the project)

The dataset has **no Order Id** — the grain is the **order-item shipment line**
(180,519 rows; a multi-item order appears once per item, and item-level
financial fields confirm it). Consequences, applied consistently:

- Every KPI is per-shipment-line, and labeled as such.
- "On-time delivery rate" = % of shipment lines delivered no later than
  scheduled, not % of distinct orders (impossible without an order key).
- Financial exposure sums item-level `Sales` (the dataset's own line measure).

## 3. Classification (official Phase 4, unchanged)

```
gap = Days for shipping (real) − Days for shipment (scheduled)
gap < 0 → Early | gap = 0 → On-time | gap > 0 → Delayed
```

Validated: gap spans −2..+4; counts 43,366 / 33,753 / 103,400 (pinned in
tests). "On-time" is never silently redefined.

## 4. Canceled shipments (documented, not deleted)

7,754 rows carry `Delivery Status = 'Shipping canceled'` yet still have gap
values. Deleting them would break reproducibility of the official basis;
keeping them unflagged would inflate "delivered" rates. Decision:

- **Official KPIs: all rows** (the spec's basis).
- **Sensitivity view: delivered-only** (canceled excluded).
- Verified: the headline delayed rate barely moves (57.28% → 57.29%), so
  conclusions are robust to the choice.

## 5. Late_delivery_risk vs the classification

Verified findings (tests/test_kpis.py::test_risk_vs_classification):

- risk=1 count (98,977) **equals** the 'Late delivery' status count exactly.
- Every gap-delayed-but-risk-0 row (4,423) is a **canceled** shipment.
- Conclusion: the flag is internally consistent; the two views differ only
  in canceled-shipment handling. This answers problem-statement gap #4.

## 6. Index design (why no composite scores)

The spec asks for delay comparison across modes and regions but warns against
arbitrary scores. Decision: **Efficiency Index = 100% − delayed%** (mode) and
**delayed share + volume + count** (region). Both are transparent,
single-formula metrics; every component is displayed beside them. A weighted
composite would add no information and hide the inputs.

## 7. Statistical language

Delays are *associated with* modes/markets; no causal claims are made (mode
assignment is not random). Financial figures are **exposure** (value shipped
on delayed lines), never "loss" — the dataset has no penalty, refund or churn
data to support loss claims.

## 8. Python ↔ SQL parity

`sql/kpis.sql` and `sql/analysis.sql` mirror `src/kpis.py` and
`src/analytics.py` formula-for-formula. Python results are pinned by 21
tests; the SQL is the portable expression of the same logic (run it against
the schema in sql/schema.sql loaded with data/processed/apl_clean.csv).

## 9. Reproducibility

```
python scripts/01_clean_data.py     # raw -> processed + quality report
python scripts/02_analysis_report.py # all analyses -> reports/analysis_report.md
python -m pytest tests/ -q           # 21 tests, all numbers pinned
```

## 10. What this project deliberately does NOT do

No ML model (the spec's conclusion positions this analysis as the foundation
*before* predictive work — a model would be premature here and is listed in
Future Scope). No date analysis (no date column exists — flagged, not faked).
No order-level metrics (no order key exists — documented).
