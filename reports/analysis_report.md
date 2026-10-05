# APL Logistics — Delivery Performance Analysis Report

## 1. Overall delivery performance (official, all-rows basis)

- Shipments: **180,519**
- Early: **43,366 (24.02%)** | On-time (== scheduled): **33,753 (18.7%)** | Delayed: **103,400 (57.28%)**
- **KPI 1 — On-time delivery rate (delivered no later than scheduled): 42.72%** (strict == scheduled: 18.7%)
- **KPI 2 — Average delivery delay (mean gap): 0.566 days** (median 1, p90 2, delay-among-delayed 1.617 days)
- **KPI 3 — Late delivery risk ratio: 54.83%** (98,977 shipments flagged)

Sensitivity (delivered-only basis, excludes 7,754 canceled): delayed 57.29% | on-time-or-early 42.71% — the headline rate is stable across bases.

## 2. Delivery gap distribution

| gap_days | shipments | pct |
| --- | --- | --- |
| -2 | 21,666 | 12.00 |
| -1 | 21,700 | 12.02 |
| 0 | 33,753 | 18.70 |
| 1 | 60,647 | 33.60 |
| 2 | 28,718 | 15.91 |
| 3 | 7,052 | 3.91 |
| 4 | 6,983 | 3.87 |

## 3. Late_delivery_risk vs calculated classification

- Gap-delayed: **103,400 (57.28%)** | risk=1: **98,977 (54.83%)**
- Both delayed AND risk=1: **98,977**
- Delayed but risk=0: **4,423** — status breakdown: {'Shipping canceled': 4423}
- risk=1 count equals 'Late delivery' status count: **True**

**Finding:** the dataset's risk flag maps exactly to Delivery Status = 'Late delivery', and every disagreement with the gap classification is a *canceled* shipment. The risk flag is consistent; the two bases differ only in how canceled shipments are handled.

## 4. Shipping mode efficiency (KPI 4 — efficiency index = 100% − delayed%)

| Shipping Mode | volume | delayed | on_time | early | avg_gap_days | avg_delay_when_delayed_days | risk_ratio | sales_exposure | volume_pct | delayed_pct | efficiency_index_pct | risk_ratio_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Standard Class | 107,752 | 42,851 | 21,535 | 43,366 | -0.00 | 1.51 | 0.38 | 22,022,391.00 | 59.70 | 39.77 | 60.23 | 38.07 |
| Second Class | 35,216 | 28,078 | 7,138 | 0 | 1.99 | 2.50 | 0.77 | 7,145,445.00 | 19.50 | 79.73 | 20.27 | 76.63 |
| First Class | 27,814 | 27,814 | 0 | 0 | 1.00 | 1.00 | 0.95 | 5,674,370.00 | 15.40 | 100.00 | 0.00 | 95.32 |
| Same Day | 9,737 | 4,657 | 5,080 | 0 | 0.48 | 1.00 | 0.46 | 1,942,529.00 | 5.40 | 47.83 | 52.17 | 45.74 |

**Findings (observed associations, not causal claims):**
- **First Class is 100.00% delayed** (27,814 of 27,814) across every market — a systematic scheduling problem, not a regional one.
- **Second Class: 79.73% delayed** with the highest average delay when delayed (2.50 days).
- **Standard Class is the most efficient** (60.23% on-time-or-early) despite carrying 59.7% of volume.
- Same Day (the premium mode) is only 52.17% on-time-or-early — and is the smallest volume mode (5.4%).

## 5. Delayed % by market × shipping mode

| Market | First Class | Same Day | Second Class | Standard Class |
| --- | --- | --- | --- | --- |
| Africa | 100.00 | 47.50 | 80.00 | 40.00 |
| Europe | 100.00 | 48.60 | 80.00 | 39.90 |
| LATAM | 100.00 | 51.10 | 78.90 | 39.60 |
| Pacific Asia | 100.00 | 44.80 | 80.40 | 39.90 |
| USCA | 100.00 | 45.10 | 79.50 | 39.50 |

The First Class pattern is uniform across all five markets — confirming a mode-level (systemic) driver rather than a regional one.

## 6. Regional delay index (KPI 5, high-volume regions ≥ 3,000 shipments)

| Order Region | volume | delayed | avg_gap_days | risk_ratio_pct | sales_exposure | delayed_pct |
| --- | --- | --- | --- | --- | --- | --- |
| Western Europe | 27,109 | 15,863 | 0.60 | 55.85 | 5,894,381.00 | 58.52 |
| South Asia | 7,731 | 4,523 | 0.60 | 56.27 | 1,553,681.00 | 58.50 |
| South of  USA | 4,045 | 2,350 | 0.58 | 55.77 | 785,784.00 | 58.10 |
| Southeast Asia | 9,539 | 5,531 | 0.56 | 55.53 | 1,932,496.00 | 57.98 |
| East of USA | 6,915 | 4,009 | 0.58 | 55.66 | 1,371,112.00 | 57.98 |
| West Asia | 6,009 | 3,455 | 0.57 | 55.28 | 1,174,672.00 | 57.50 |
| Eastern Europe | 3,920 | 2,252 | 0.58 | 55.66 | 774,267.00 | 57.45 |
| Central America | 28,341 | 16,224 | 0.56 | 54.75 | 5,665,712.00 | 57.25 |
| South America | 14,935 | 8,548 | 0.56 | 54.31 | 2,960,881.00 | 57.23 |
| US Center | 5,887 | 3,363 | 0.59 | 55.24 | 1,151,356.00 | 57.13 |
| Southern Europe | 9,431 | 5,350 | 0.52 | 54.38 | 2,047,919.00 | 56.73 |
| Eastern Asia | 7,280 | 4,130 | 0.57 | 54.33 | 1,486,401.00 | 56.73 |
| North Africa | 3,232 | 1,832 | 0.55 | 54.52 | 634,752.00 | 56.68 |
| West of USA | 7,993 | 4,524 | 0.56 | 53.96 | 1,571,416.00 | 56.60 |
| Northern Europe | 9,792 | 5,524 | 0.55 | 54.04 | 2,155,831.00 | 56.41 |
| Oceania | 10,148 | 5,694 | 0.56 | 54.02 | 2,016,654.00 | 56.11 |
| Caribbean | 8,318 | 4,648 | 0.55 | 53.08 | 1,651,019.00 | 55.88 |
| West Africa | 3,696 | 2,033 | 0.55 | 52.84 | 727,951.00 | 55.01 |

**Finding:** regional variation is narrow (≈55–58.5% delayed among high-volume regions). Delay is systemic across the network — the dominant driver is shipping mode, not geography. Western Europe is the worst high-volume region (58.52% delayed, 27,109 shipments); West Africa the best of the ≥3,000 group (55.01%).

## 7. Market analysis

| Market | volume | delayed | avg_gap_days | risk_ratio_pct | sales | delayed_pct |
| --- | --- | --- | --- | --- | --- | --- |
| Europe | 50,252 | 28,989 | 0.57 | 55.21 | 10,872,396.60 | 57.69 |
| Pacific Asia | 41,260 | 23,649 | 0.57 | 55.05 | 8,273,743.58 | 57.32 |
| USCA | 25,799 | 14,744 | 0.57 | 54.80 | 5,066,528.61 | 57.15 |
| LATAM | 51,594 | 29,420 | 0.56 | 54.36 | 10,277,612.64 | 57.02 |
| Africa | 11,614 | 6,598 | 0.56 | 54.59 | 2,294,452.88 | 56.81 |

## 8. Customer segment analysis

| Customer Segment | volume | delayed | risk_ratio_pct | sales | avg_profit_per_order | delayed_pct |
| --- | --- | --- | --- | --- | --- | --- |
| Consumer | 93,504 | 53,573 | 54.81 | 19,095,790.00 | 22.18 | 57.29 |
| Corporate | 54,789 | 31,291 | 54.72 | 11,168,407.00 | 21.95 | 57.11 |
| Home Office | 32,226 | 18,536 | 55.07 | 6,520,538.00 | 21.44 | 57.52 |

**Finding:** delivery performance is statistically uniform across Consumer, Corporate and Home Office (≈57% delayed each). No customer segment is disproportionately affected — there is no 'premium penalty' in this dataset. (The dataset has three generic segments; enterprise/premium tiers do not exist here.)

## 9. Financial exposure (associated value — NOT confirmed loss)

- Sales associated with delayed shipments: **$21,025,185 of $36,784,734 (57.16%)**
- Profit-per-order associated with delayed shipments: $2,231,967 of $3,966,903

The dataset does not support causal loss claims (no penalty, churn or refund data). 'Exposure' = value shipped on delayed legs.
