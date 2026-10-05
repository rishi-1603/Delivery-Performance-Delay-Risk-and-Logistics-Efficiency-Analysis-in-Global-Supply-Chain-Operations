# KPI Dictionary — exact definitions, formulas, and bases

Every KPI is computed in `src/kpis.py`, mirrored in `sql/kpis.sql`, and pinned
by `tests/test_kpis.py`. Two **bases** are used throughout:

- **all** (official): all 180,519 shipment rows
- **delivered** (sensitivity): excludes the 7,754 'Shipping canceled' rows

The headline rates are stable across both bases (delayed: 57.28% vs 57.29%).

---

## KPI 1 — On-Time Delivery Rate

**Definition:** % of shipments delivered **no later than scheduled**.
**Formula:** `(Early + On-time) / Total` where the classification is
`gap = Days for shipping (real) − Days for shipment (scheduled)` and
`Early: gap < 0 · On-time: gap = 0 · Delayed: gap > 0`.
**Basis:** all rows (primary); delivered-only (sensitivity).
**Verified values:** 42.72% (all) / 42.71% (delivered). Strict variant
(delivered exactly on the scheduled day): 18.70%.
**Limitation:** "within scheduled time" is defined as *not later than*
scheduled; the strict-equal variant is always reported alongside.

## KPI 2 — Average Delivery Delay

**Definition:** Mean of the delivery gap across all shipments in scope.
**Formula:** `AVG(real − scheduled)`. Early deliveries are **not** clipped
to zero — clipping would hide the early-delivery offset and change the
meaning of the metric.
**Verified values:** 0.566 days (mean) · median 1 · p90 2 ·
mean-among-delayed 1.617 days · avg actual shipping days for delayed
shipments 4.09.
**Limitation:** a mean near zero is a mix of early (−2/−1) and delayed
(+1..+4) shipments — always read with the distribution (Section 2 of the
analysis report).

## KPI 3 — Late Delivery Risk Ratio

**Definition:** Share of shipments with the dataset's own
`Late_delivery_risk = 1`.
**Formula:** `SUM(risk) / COUNT(*)`.
**Verified value:** 54.83% (98,977 of 180,519).
**Relationship to KPI 1:** risk=1 maps **exactly** to Delivery Status
'Late delivery' (verified: counts equal). The gap-classification flags
103,400 delayed; the extra 4,423 are all *canceled* shipments. This is a
verified analytical finding, not an error.

## KPI 4 — Shipping Mode Efficiency

**Definition:** Transparent per-mode comparison; the **Efficiency Index**
is simply the on-time-or-early share (= 100% − delayed%). No arbitrary
weighting — volume, delayed count, average gap, delay-when-delayed, risk
ratio, and sales exposure are all shown beside it.
**Verified values (all basis):**

| Mode | Volume | Delayed % | Efficiency Index | Risk ratio |
|---|---|---|---|---|
| Standard Class | 107,752 | 39.77% | 60.23% | 38.07% |
| Second Class | 35,216 | 79.73% | 20.27% | 76.63% |
| First Class | 27,814 | **100.00%** | 0.00% | 95.32% |
| Same Day | 9,737 | 47.83% | 52.17% | 45.74% |

**Limitation:** association, not causation — mode assignment is not random
in this dataset.

## KPI 5 — Regional Delay Index

**Definition:** Delayed share by `Order Region`, **always shown with volume
and delayed count** so small-sample regions are never misread (a 90% delay
rate on 10 shipments is not a network problem; a 40% rate on 100,000 is).
**Verified range:** ≈55–58.5% among high-volume (≥3,000) regions — the
narrow spread shows delay is **systemic (mode-driven), not regional**.
Worst high-volume region: Western Europe (58.52%, 27,109 shipments).
