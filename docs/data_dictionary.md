# Data Dictionary — APL Logistics dataset

**Source:** `data/raw/APL_Logistics.csv` (latin-1) → cleaned to `data/processed/apl_clean.csv` (utf-8)
**Grain:** one row = one **order-item shipment line** (180,519 rows). There is **no Order Id** column, so order-level aggregation is impossible — every KPI in this project is per-shipment-line and documented as such.

## Delivery fields (the analytical core)

| Column | Type | Description |
|---|---|---|
| Days for shipping (real) | int | Actual shipping duration in days |
| Days for shipment (scheduled) | int | Planned/Scheduled duration in days |
| Delivery Status | text | `Advance shipping` / `Late delivery` / `Shipping canceled` / `Shipping on time` |
| Late_delivery_risk | int 0/1 | The dataset's own late-risk flag (maps 1:1 to Delivery Status = 'Late delivery' — verified) |
| Shipping Mode | text | `Standard Class` / `Second Class` / `First Class` / `Same Day` |
| Order Status | text | `COMPLETE` / `PENDING_PAYMENT` / `PROCESSING` / `PENDING` / `CLOSED` / `ON_HOLD` / `SUSPECTED_FRAUD` / `CANCELED` / … |

## Derived columns (computed in the pipeline, mirrored in SQL)

| Column | Formula | Notes |
|---|---|---|
| delivery_delay_gap | real − scheduled | Official Phase-4 definition |
| delivery_class | Early (<0) / On-time (=0) / Delayed (>0) | Official classification |
| is_canceled | Delivery Status = 'Shipping canceled' | 7,754 rows — flagged, never deleted |

## Geography

| Column | Description |
|---|---|
| Market | 5 values: Pacific Asia, LATAM, USCA, Europe, Africa |
| Order Region | 23 regions (e.g., Western Europe, Central America, South Asia) |
| Order Country / Order State / Order City | 164 countries; accented names preserved (e.g., México) |
| Customer Country | 2 values after standardization: United States (was 'EE. UU.'), México |
| Latitude / Longitude | Customer geolocation |

## Customer & product

| Column | Description |
|---|---|
| Customer Id / Order Customer Id | 20,652 unique customers (the two columns map 1:1) |
| Customer Segment | Consumer (93,504) / Corporate (54,789) / Home Office (32,226) — no enterprise/premium tier exists |
| Category Name / Category Id | 50 categories |
| Department Name | 11 departments |
| Product Name / Product Price | 118 products |
| Order Item Quantity / Order Item Product Price / Order Item Discount / Order Item Discount Rate / Order Item Total / Order Item Profit Ratio | Item-level economics |

## Financial measures

| Column | Description |
|---|---|
| Sales | Item sales value (min $10, max $2,000; mean $203.77) |
| Sales per customer | Sales net of discount |
| Order Item Total | Item total after discount |
| Order Profit Per Order / Benefit per order | Per-order profit (identical distributions; 33,784 negative values = loss-making lines) |
| Type | Payment type (DEBIT / CREDIT / TRANSFER / PAYMENT, incl. some CASH) |

## Known limitations (documented, not 'fixed')

1. **No date column** — a date-range filter is not supported by this dataset.
2. **No Order Id** — grain is order-item; order-level KPIs impossible.
3. **Canceled shipments (7,754)** carry gap values; flagged and reported on both bases.
4. **'EE. UU.'** standardized to 'United States' (documented transformation).
5. **Customer Lname (8 missing), Customer Zipcode (3 missing)** — left as-is; neither affects delivery KPIs.
6. Names/addresses are present in the raw file (customer PII in a public dataset) — the processed file keeps them because the spec requires customer-level analysis; they are never displayed in aggregates.
