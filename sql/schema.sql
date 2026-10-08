-- ============================================================
--  schema.sql — the shipments table as it exists after the
--  cleaning pipeline (data/processed/apl_clean.csv).
--
--  Load the processed CSV as the `shipments` table and every
--  query in kpis.sql / analysis.sql runs as-is (verified against
--  src/kpis.py — see the audit trail in the repo history):
--
--    SQLite:   .mode csv
--              .import data/processed/apl_clean.csv shipments
--
--  Column names are kept EXACTLY as shipped (quoted identifiers):
--  raw columns preserve their original casing; the 3 derived
--  columns are lowercase. Nothing is renamed on load.
-- ============================================================

CREATE TABLE shipments (
    "Type"                          TEXT,      -- DEBIT / TRANSFER / PAYMENT / CASH
    "Days for shipping (real)"      INTEGER,   -- actual shipping duration
    "Days for shipment (scheduled)" INTEGER,   -- planned duration
    "Benefit per order"             REAL,
    "Sales per customer"            REAL,
    "Delivery Status"               TEXT,      -- Late delivery / Advance shipping / Shipping on time / Shipping canceled
    "Late_delivery_risk"            INTEGER,   -- dataset's own 0/1 flag (maps exactly to 'Late delivery')
    "Market"                        TEXT,      -- Pacific Asia / LATAM / USCA / Europe / Africa
    "Order Region"                  TEXT,      -- 23 regions
    "Order Country"                 TEXT,
    "Order State"                   TEXT,
    "Order Status"                  TEXT,
    "Order Profit Per Order"        REAL,
    "Order Item Total"              REAL,
    "Sales"                         REAL,
    "Customer Segment"              TEXT,      -- Consumer / Corporate / Home Office
    "Customer Country"              TEXT,      -- 'EE. UU.' standardized to 'United States'
    "Latitude"                      REAL,
    "Longitude"                     REAL,
    -- ── derived by the pipeline (documented, test-pinned) ──
    delivery_delay_gap              INTEGER,   -- real − scheduled
    delivery_class                  TEXT,       -- Early (<0) / On-time (=0) / Delayed (>0)
    is_canceled                     INTEGER     -- Delivery Status = 'Shipping canceled' (7,754 rows)
    -- …plus remaining raw columns, unchanged (see docs/data_dictionary.md)
);

CREATE INDEX idx_shipments_mode  ON shipments("Shipping Mode");
CREATE INDEX idx_shipments_region ON shipments("Order Region");
CREATE INDEX idx_shipments_gap   ON shipments(delivery_delay_gap);
