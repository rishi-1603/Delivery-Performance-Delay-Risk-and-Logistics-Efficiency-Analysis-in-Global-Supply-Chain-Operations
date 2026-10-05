# Research Paper: Delivery Performance, Delay Risk, and Logistics Efficiency Analysis in Global Supply Chain Operations

**Author:** Dappu Rishi Raghukumar — B.Tech CSE (Data Science), 2026
**Domain:** Supply Chain Analytics / Logistics Operations
**Dataset:** 180,519 order-item shipment lines (APL Logistics / DataCo, from the official project specification)

---

## Abstract

This study analyzes 180,519 shipment lines across 23 regions, 5 markets, and 4 shipping modes to measure delivery performance, diagnose delay drivers, and quantify financial exposure for APL Logistics (KWE Group). Using the official delivery gap definition (actual shipping days minus scheduled shipping days), we find that **57.28% of shipments are delayed**, with an average delay of 0.566 days and $21.0M in sales exposure. The analysis reveals a striking finding: **First Class shipping is 100.00% delayed across every market**, indicating a systematically unachievable scheduling promise rather than a regional problem. We demonstrate that delay is **mode-driven, not geography-driven** — mode delayed rates span 60 percentage points while regional rates span only 3.5. The dataset's `late_delivery_risk` flag is shown to be internally consistent, mapping exactly to the 'Late delivery' status, with all disagreements attributable to canceled shipments. We provide five KPIs, a transparent shipping-mode efficiency index, and volume-aware regional diagnostics, establishing the analytical foundation for predictive and optimization models.

---

## 1. Introduction

Delivery delays lead to SLA violations, penalties, and customer dissatisfaction in global logistics. Despite having detailed shipment data, organizations often lack clear on-time measurement, understanding of delay drivers, and visibility into high-risk modes and regions. This project addresses four specific gaps identified by APL Logistics: (1) clear on-time vs delayed measurement, (2) understanding of why shipments are delayed, (3) visibility into high-risk regions and modes, and (4) diagnostics for the `late_delivery_risk` flag.

## 2. Business Context

APL Logistics (KWE Group) handles high-volume, multi-region shipments. Delivery performance monitoring is critical for operational excellence. The organization operates reactively rather than preventively because it lacks the analytical infrastructure to identify delay patterns before they become SLA violations.

## 3. Problem Statement

Despite detailed order and shipping data, the organization lacks clear measurement of on-time vs delayed deliveries, understanding of delay drivers, visibility into high-risk modes and regions, and diagnostics for the late_delivery_risk flag. This analysis directly addresses these four gaps.

## 4. Objectives

1. Implement the official delivery classification (Early/On-time/Delayed) and measure the on-time delivery rate.
2. Quantify average delivery delay and the late-delivery-risk ratio.
3. Compare shipping mode efficiency and regional delay patterns.
4. Diagnose the relationship between the calculated delay classification and the dataset's `late_delivery_risk` flag.
5. Quantify the financial exposure associated with delayed shipments.

## 5. Dataset Description

| Property | Value |
|---|---|
| Rows | 180,519 (order-item shipment lines) |
| Columns | 40 raw + 3 derived |
| Grain | Order-item (no Order Id — documented limitation) |
| Regions | 23 | Markets | 5 |
| Countries | 164 (order) | Products | 118 |
| Customers | 20,652 | Shipping modes | 4 |
| Date columns | **None** (no trend analysis possible) |
| Encoding | latin-1 (accented names) |
| Duplicates | 0 exact duplicates |

### Data Quality

The dataset is clean by portfolio standards: 0 exact duplicates, near-zero missing values (8 Lastname, 3 Zipcode), and consistent categorical values. Two issues were addressed: 'EE. UU.' in Customer Country (Spanish for USA) was standardized to 'United States', and 7,754 canceled shipments were flagged (never deleted) so that delivery KPIs could be reported on both the official all-rows basis and a delivered-only sensitivity basis.

## 6. Data Cleaning

A reproducible pipeline (`src/data_cleaning.py`) applies 10 logged transformations: whitespace stripping, duplicate verification, country standardization, numeric validation, risk-domain validation, delivery gap calculation, classification, canceled-shipment flagging, and missing-value documentation. No records are deleted; canceled shipments are flagged.

## 7. Analytical Methodology

### 7.1 Delivery Gap and Classification

```
gap = Days for shipping (real) - Days for shipment (scheduled)
gap < 0 → Early | gap = 0 → On-time | gap > 0 → Delayed
```

### 7.2 KPI Definitions

| KPI | Formula | Basis |
|---|---|---|
| On-time delivery rate | (Early + On-time) / Total | All rows (primary) |
| Average delivery delay | AVG(real - scheduled) | All rows |
| Late delivery risk ratio | SUM(risk=1) / COUNT(*) | All rows |
| Mode efficiency index | 100% - delayed% | Per mode |
| Regional delay index | delayed% (with volume) | Per region |

### 7.3 Grain Decision

The dataset has no Order Id; the grain is order-item. All KPIs are per-shipment-line and documented as such.

## 8. Exploratory Data Analysis

The delivery gap distribution is discrete and bounded: -2 to +4 days. The modal gap is +1 day (33.6% of shipments), followed by 0 days (18.7%) and -1 day (12.0%). The distribution is right-skewed: more mass above zero than below, driving the 57.28% delayed rate.

## 9. Delivery Performance Analysis

### Overall

| Classification | Count | % |
|---|---|---|
| Early | 43,366 | 24.02% |
| On-time | 33,753 | 18.70% |
| Delayed | 103,400 | **57.28%** |

### Risk vs Classification (Key Finding)

The `late_delivery_risk` flag maps **exactly** to Delivery Status = 'Late delivery' (98,977 = 98,977). Every disagreement with the gap classification (4,423 shipments) is a canceled shipment. This resolves the problem statement's gap #4: the flag is internally consistent and can be trusted for monitoring.

## 10. Shipping Mode Analysis

| Mode | Volume | Delayed % | Avg Gap | Risk Ratio |
|---|---|---|---|---|
| Standard Class | 107,752 | 39.77% | -0.00 | 38.07% |
| Second Class | 35,216 | 79.73% | 1.99 | 76.63% |
| First Class | 27,814 | **100.00%** | 1.00 | 95.32% |
| Same Day | 9,737 | 47.83% | 0.48 | 45.74% |

**First Class is 100% delayed in every market** — a mode-level systemic issue, not regional.

## 11. Regional & Market Analysis

Regional delayed rates span only ~3.5 percentage points among high-volume regions (55.0%–58.5%), compared to 60 pp across modes. Delay is systemic. Western Europe is the worst high-volume region (58.52%, 27,109 shipments).

## 12. Customer Segment Analysis

Consumer (57.29%), Corporate (57.11%), and Home Office (57.52%) segments show statistically uniform delayed rates. No segment is disproportionately affected.

## 13. Key Findings

1. 57.28% of shipments are delayed; $21.0M (57.2%) of sales value is exposed.
2. First Class shipping is 100% delayed across all markets — a scheduling design failure.
3. Delay is mode-driven (60 pp spread), not regional (3.5 pp spread).
4. The late_delivery_risk flag is consistent (maps exactly to 'Late delivery' status).
5. Customer segment performance is uniform — no premium penalty.

## 14. Business Recommendations

| Finding | Impact | Recommendation | Priority |
|---|---|---|---|
| First Class 100% delayed | 15.4% of volume, $5.7M exposure | Audit scheduled-time promises and carrier SLAs | HIGH |
| Second Class 79.7% delayed | 19.5% of volume | Review scheduling accuracy | HIGH |
| Standard Class most efficient | 59.7% of volume, best on-time rate | Shift eligible volume to Standard | MEDIUM |
| Canceled shipments in KPIs | 4,423 misclassified as delayed | Exclude from delivery KPIs | MEDIUM |

## 15. Limitations

- No date column — trend and seasonality analysis is impossible.
- No Order Id — order-level KPIs cannot be computed; all rates are per-line.
- Static dataset — no refresh or real-time monitoring.
- No penalty/refund/churn data — financial figures are exposure, not loss.
- Synthetic/public dataset (DataCo) — real-world generalization requires validation.

## 16. Future Scope

Per the official project conclusion, this analysis is the foundation before predictive work: delivery delay prediction, carrier risk scoring, route optimization, capacity optimization, dynamic mode recommendation, SLA-breach early warning. None are implemented here — by design.

## 17. Conclusion

This project transforms raw shipment data into operational intelligence for APL Logistics. The most important insight — that delay is mode-driven rather than geography-driven — redirects the operational conversation from regional firefighting to mode-policy reform. The 100% First Class delay rate is the single most actionable finding: it represents a systematically broken promise, not a performance problem. With 21 automated tests pinning every number, the analysis is reproducible and defensible in any operational review.

---

*Every number in this paper is computed from the dataset and pinned by automated tests in `tests/`. The full analysis with all tables is in `reports/analysis_report.md`.*
