# Executive Summary — APL Logistics Delivery Performance Analysis

**Prepared for:** Logistics Operations Leadership, APL Logistics (KWE Group)
**Data:** 180,519 order-item shipment lines · 23 regions · 5 markets · 164 countries · 4 shipping modes
**All numbers are computed from the dataset and pinned by 23 automated tests.**

---

## 1. Current delivery performance

| Metric | Value |
|---|---|
| On-time delivery rate (delivered no later than scheduled) | **42.72%** |
| Strict on-time (exactly on scheduled day) | 18.70% |
| Delayed shipments | **103,400 (57.28%)** |
| Average delivery delay (mean gap) | **0.566 days** |
| Average delay among delayed shipments | 1.617 days |
| Late-delivery-risk ratio (dataset flag) | **54.83%** (98,977 shipments) |
| Sales associated with delayed shipments | **$21.0M of $36.8M (57.2%)** |

## 2. How large is the delay problem?

Over half of all shipment lines arrive later than scheduled. $21M in sales value rides on delayed legs — this is exposure, not confirmed loss (the dataset has no penalty or refund data). The average delayed shipment arrives 1.6 days late.

## 3. Which shipping modes are problematic?

| Mode | Volume | Delayed % | Assessment |
|---|---|---|---|
| **First Class** | 27,814 | **100.00%** | 🔴 Structurally broken — every shipment delayed, in every market |
| **Second Class** | 35,216 | **79.73%** | 🔴 Severe — 4 in 5 delayed, worst avg delay (2.50d) |
| **Same Day** | 9,737 | 47.83% | 🟡 Moderate — underperforms for a premium mode |
| **Standard Class** | 107,752 | **39.77%** | 🟢 Best mode — handles 59.7% of volume most efficiently |

## 4. Which regions/markets are high risk?

Regional variation is **narrow** (~55–58.5% delayed among high-volume regions) — delay is **systemic (mode-driven), not regional**. Western Europe is the worst high-volume region (58.52%, 27,109 shipments). No region or market requires targeted intervention; the lever is mode policy.

## 5. Which customer segments are affected?

Delivery performance is **uniform** across Consumer, Corporate and Home Office (~57% delayed each). No segment is disproportionately impacted. (The dataset has three generic segments; enterprise/premium tiers do not exist.)

## 6. Most important operational findings

1. **First Class is 100% delayed** — 27,814 of 27,814, uniformly across all 5 markets. The scheduled-time promise for this mode is systematically unachievable. $5.7M in sales exposure.
2. **Delay is mode-driven, not geography-driven.** Mode rates span 60 pp; regional rates span 3.5 pp. Mode allocation policy is the lever, not regional firefighting.
3. **The dataset's risk flag is consistent and fully explained.** risk=1 maps exactly to 'Late delivery' status (98,977 = 98,977). All 4,423 disagreements with the gap classification are canceled shipments.

## 7. What management should prioritize

| Priority | Action | Expected benefit |
|---|---|---|
| 🔴 HIGH | Audit First Class scheduled-time promises and carrier SLAs | Addresses 15.4% of volume at 100% delay rate |
| 🔴 HIGH | Review Second Class scheduling accuracy | 19.5% of volume at 79.7% delay |
| 🟡 MED | Shift eligible volume to Standard Class (most efficient mode) | Best on-time performance at highest volume |
| 🟡 MED | Exclude canceled shipments from delivery KPIs (4,423 misclassified) | Cleaner operational reporting |
| 🟢 LOW | Regional monitoring (Western Europe worst at 58.5%) | Narrow spread suggests limited ROI |
