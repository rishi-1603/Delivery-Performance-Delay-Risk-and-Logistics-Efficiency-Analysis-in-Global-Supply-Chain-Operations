# Data Quality Report

Source: `data/raw/APL_Logistics.csv` (encoding: latin-1) | Processed: `data/processed/apl_clean.csv` (utf-8)

## Transformation log

| Step | Detail |
|---|---|
| load | 180,519 rows x 40 columns read (latin-1) |
| whitespace | stripped leading/trailing whitespace in 23373 cell(s) across text columns |
| duplicates | 0 exact duplicate rows found (expected 0; nothing deleted) |
| standardize_country | Customer Country: 111,146 rows 'EE. UU.' -> 'United States' (Spanish spelling; Order Country accents preserved as-is) |
| numeric_validation | Days for shipping (real) / (scheduled): all non-negative integers — pass |
| risk_domain | Late_delivery_risk in {0,1} for all rows — pass |
| delivery_gap | delivery_delay_gap = Days for shipping (real) - Days for shipment (scheduled) |
| classification | delivery_class: Early (gap<0) / On-time (gap==0) / Delayed (gap>0) |
| cancel_flag | 7,754 rows flagged is_canceled (Delivery Status == 'Shipping canceled') — kept in data; excluded only in the documented delivered-basis sensitivity view |
| missing_values | left as-is (not imputed): Customer Lname (8), Customer Zipcode (3) — none affect delivery KPIs |
| write | processed dataset written to apl_clean.csv (utf-8) |

## Dataset profile

- Rows: 180,519 (order-item grain — see methodology)
- Columns: 43 (40 raw + 3 derived)
- Exact duplicate rows: 0
- Unique customers: 20,652
- Order Regions: 23 | Markets: 5 | Order Countries: 164
- Shipping Modes: 4 | Categories: 50

## Known limitations (documented, not 'fixed')

1. **No date column** — a date-range filter is NOT supported by this dataset.
2. **No Order Id** — the grain is order-ITEM; order-level KPIs are impossible.
   All rates are per-shipment-row and documented as such.
3. **Canceled shipments (7,754 rows)** carry gap values; they are flagged,
   never deleted. Official KPIs use the all-rows basis; a delivered-only
   sensitivity view is provided alongside.
4. **'EE. UU.'** in Customer Country (Spanish for USA) standardized to
   'United States'; accented Order Country names preserved.
5. Missing values (8 Customer Lname, 3 Customer Zipcode) left as-is —
   neither affects delivery KPIs.