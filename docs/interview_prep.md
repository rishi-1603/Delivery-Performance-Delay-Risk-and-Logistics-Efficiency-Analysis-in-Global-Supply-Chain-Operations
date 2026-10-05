# Interview Preparation — APL Logistics Delivery Analytics

## Core project explanation (30-second version)

"I analyzed 180,519 shipment lines for APL Logistics to measure delivery performance, diagnose delay drivers, and quantify financial exposure. I found that 57% of shipments are delayed, with $21M in sales exposure. The most striking finding: First Class shipping is 100% delayed in every market — a systemic scheduling problem, not a regional one. I built a KPI engine, a Streamlit dashboard, a SQL layer, and 21 tests that pin every number to the dataset."

## Key questions and answers

### "Why did you choose this problem?"
The official project specification identified four gaps: no on-time measurement, no delay-driver understanding, no mode/region visibility, no risk-flag diagnostics. Every analysis maps to one of those four.

### "How did you calculate the delivery gap?"
Official definition: gap = Days for shipping (real) - Days for shipment (scheduled). Negative = Early, zero = On-time, positive = Delayed. I never redefined "on-time."

### "Why did you use actual minus scheduled?"
That's the official spec's Phase 4 definition. It's the most direct measure of SLA adherence — how many days the shipment deviated from the promise.

### "How did you define on-time?"
Two definitions, both documented: "delivered no later than scheduled" (primary, 42.72%) and "exactly on the scheduled day" (strict, 18.70%). Both are reported so the reader can choose their interpretation.

### "What is late_delivery_risk?"
The dataset's own binary flag (0/1). I verified it maps exactly to Delivery Status = 'Late delivery' (98,977 = 98,977). The only disagreements with my gap classification are 4,423 canceled shipments — the flag is internally consistent.

### "Why didn't you build an ML model?"
The spec's conclusion positions this analysis as the foundation *before* predictive work. A model would be premature — we first need to understand what's happening and why. Future scope includes delay prediction, but this project is deliberately descriptive/diagnostic.

### "How did you validate your KPIs?"
21 pytest tests pin every headline number to the dataset. The SQL layer mirrors the Python formulas exactly. I also ran a sensitivity check (delivered-only vs all-rows basis) confirming the headline rate is stable (57.28% vs 57.29%).

### "How did you handle duplicate orders?"
The dataset has no Order Id — the grain is order-item (one row per item in a multi-item order). I verified there are 0 exact duplicate rows. Financial fields are item-level, so summing them doesn't double-count.

### "What was your biggest data-quality issue?"
7,754 'Shipping canceled' rows carry delivery gap values. If included naively, they inflate the "delayed" count. I flagged them (never deleted) and reported KPIs on both bases: all-rows (official) and delivered-only (sensitivity). The headline rate barely changes (57.28% → 57.29%), making the conclusions robust.

### "Which shipping mode performed worst?"
First Class — 100.00% delayed (27,814 of 27,814 shipments), in every single market. That's not a performance issue; it's a scheduling-design failure. The scheduled-time promise for First Class is systematically unachievable.

### "Which region had the highest delay?"
Western Europe (58.52%, 27,109 shipments) among high-volume regions. But the regional spread is only ~3.5 percentage points — delay is systemic, not regional. The lever is mode policy.

### "What would you do if management asked you to reduce delays?"
1. Audit First Class scheduled-time promises (100% delayed = broken promise)
2. Review Second Class scheduling accuracy (79.7% delayed)
3. Shift eligible volume to Standard Class (best on-time rate at highest volume)
4. Build a monitoring dashboard with the risk flag (proven consistent)

### "What would you build next?"
A delay-prediction model using the features already in the dataset (mode, market, region, segment, product category). The analysis shows mode is the dominant driver — a classifier could estimate delay probability per shipment for proactive intervention.

### "What are the limitations?"
No date column (no trend analysis), no order key (per-line not per-order), static dataset (no refresh), no penalty/refund data (exposure not loss), synthetic dataset.

## Technical questions

### "Explain your most complex SQL query."
The mode efficiency query in sql/kpis.sql uses conditional aggregation (CASE WHEN inside SUM) to compute early/on-time/delayed counts, average gap, risk ratio, and sales exposure in a single GROUP BY — mirroring the Python exactly.

### "Why did you use a window function?" 
I didn't need one for the core KPIs (the gap is a simple subtraction). PERCENTILE_CONT for median and p90 is the most advanced SQL used. I deliberately avoided unnecessary complexity.

### "How did you prevent duplicate aggregation?"
By identifying the grain first (order-item, no order key) and summing only item-level fields. The crosstab for risk vs classification uses COUNT with CASE, not JOINs.

### "How does the dashboard stay performant with 180K rows?"
@st.cache_data on the data loading and all KPI computations. The geographic scatter uses an 8,000-row sample. Plotly charts are efficient because the aggregations happen before rendering.
