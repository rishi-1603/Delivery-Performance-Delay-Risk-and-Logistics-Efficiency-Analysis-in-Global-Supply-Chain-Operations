# Delivery Performance, Delay Risk and Logistics Efficiency

A descriptive shipment-line case study using public / synthetic supply-chain data

**Author:** Dappu Rishi Raghukumar
**Project/reporting date:** 23 September 2026
**Web edition prepared:** 2 November 2026
**Status:** Unpublished project technical report; not peer-reviewed or independently approved.

## Abstract
This project examines 180,519 order-item shipment lines across five markets, 23 regions and four shipping modes. It defines early, exactly on-time and delayed lines using actual minus scheduled shipping days, compares an existing late-delivery flag with that calculation, and presents mode and regional summaries. The browser companion uses an aggregated, privacy-minimized export of the original Python pipeline. The findings describe the supplied educational dataset; they do not establish real company performance or causal delay drivers.

## Results
- Shipment lines: 180,519
- Within scheduled time (early + on-time): 42.72%
- Calculated delayed lines: 103,400 (57.28%)
- Mean actual-minus-scheduled gap: 0.566 days
- Mean positive gap among delayed lines: 1.617 days
- Existing late-delivery flag: 98,977 lines (54.83%)
- Recorded sales: USD 36,784,734.31

## 1. Question and reporting unit
The analysis asks how delivery timing differs across shipping modes, markets and regions, and whether the existing risk flag agrees with a gap-based classification. One row is an order-item shipment line. There is no order identifier supporting an independent order-level denominator, and there is no date column supporting trends or seasonality.

## 2. Data preparation
The repository loads the release CSV using latin-1 encoding, strips text whitespace, standardizes the documented EE. UU. customer-country spelling, validates numeric/risk domains and derives the gap and cancellation flag. Canceled records remain in the data. Missing non-KPI customer attributes are not silently imputed. The browser export retains only mode, region, market, segment, gap, flag, cancellation status, counts and summed sales; it excludes names, addresses, customer IDs and coordinates.

## 3. Definitions
Gap = actual shipping days minus scheduled shipping days. A negative gap is early, zero is exactly on time, and a positive gap is delayed. The primary within-schedule rate combines early and exactly on-time lines. The mean gap includes negative values; the mean positive delay is a separate measure. The existing Late_delivery_risk field is a dataset attribute, not a new prospective prediction.

## 4. Results and interpretation
First Class has a 100% positive-gap rate in the supplied data. This is a reason to investigate the relationship between the mode labels and promised durations, not proof of a real carrier failure. Mode-level delayed percentages differ more than the reported high-volume regional percentages, but those descriptive differences do not isolate causal effects. The risk flag aligns with the dataset delivery-status label; 4,423 differences from the gap-based classification relate to canceled lines. A cancellation sensitivity view is available rather than assuming canceled records represent observed completed deliveries.

## 5. Financial interpretation
Approximately USD 21 million of sales is associated with delayed lines. It is exposure, not confirmed loss, penalties, refunds or savings. The dataset does not measure those outcomes, so financial recommendations require separate evidence.

## 6. Demonstration and reproducibility
The original Streamlit application remains at dashboard/app.py. The browser companion has four sections, dimension filters, a cancellation-basis toggle and summary CSV downloads. scripts/build_web_data.py recreates its aggregate export using the existing cleaning and KPI modules. The repository contains SQL, tests and generated reports. The hosted demo is a static client-side application, not a hosted Python server.

## 7. Limitations and next validation
The supplied dataset is a public / synthetic educational case, not independently verified APL Logistics operational data. There is no longitudinal evaluation, distinct-order key, causal experiment, observed carrier cost or penalty outcome. Before operational use, confirm provenance and rights, obtain true service-level definitions and evaluate whether segment/mode mix explains the descriptive differences.

## Sources
https://github.com/rishi-1603/Delivery-Performance-Delay-Risk-and-Logistics-Efficiency-Analysis-in-Global-Supply-Chain-Operations
See the repository methodology, KPI dictionary, original analysis and data-quality reports.
