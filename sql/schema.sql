-- ============================================================
--  schema.sql — APL Logistics delivery analytics (PostgreSQL 14+)
--  Grain: one row = one order-item shipment line (180,519 rows).
--  NOTE: the raw dataset has NO Order Id — order-level aggregation
--  is impossible; every KPI below is per-shipment-line and the
--  limitation is documented in docs/methodology.md.
-- ============================================================

CREATE TABLE IF NOT EXISTS shipments (
    type                          TEXT,
    days_real                     INTEGER CHECK (days_real >= 0),
    days_scheduled                INTEGER CHECK (days_scheduled >= 0),
    benefit_per_order             NUMERIC(12,2),
    sales_per_customer            NUMERIC(12,2),
    delivery_status               TEXT,   -- Advance shipping / Late delivery / Shipping canceled / Shipping on time
    late_delivery_risk            SMALLINT CHECK (late_delivery_risk IN (0,1)),
    category_id                   INTEGER,
    category_name                 TEXT,
    customer_city                 TEXT,
    customer_country              TEXT,   -- 'EE. UU.' standardized to 'United States' in processing
    customer_id                   INTEGER,
    customer_segment              TEXT,   -- Consumer / Corporate / Home Office
    customer_state                TEXT,
    customer_zipcode              NUMERIC(10,0),
    department_name               TEXT,
    latitude                      NUMERIC(9,6),
    longitude                     NUMERIC(9,6),
    market                        TEXT,   -- Pacific Asia / LATAM / USCA / Europe / Africa
    order_city                    TEXT,
    order_country                 TEXT,
    order_item_total              NUMERIC(12,2),
    order_profit_per_order        NUMERIC(12,2),
    order_region                  TEXT,
    order_state                   TEXT,
    order_status                  TEXT,
    product_name                  TEXT,
    product_price                 NUMERIC(10,2),
    shipping_mode                 TEXT,   -- Standard Class / Second Class / First Class / Same Day
    sales                         NUMERIC(12,2),
    -- derived (computed in the Python pipeline, mirrored here)
    delivery_delay_gap            INTEGER,  -- days_real - days_scheduled
    delivery_class                TEXT CHECK (delivery_class IN ('Early','On-time','Delayed')),
    is_canceled                   BOOLEAN    -- delivery_status = 'Shipping canceled'
);
