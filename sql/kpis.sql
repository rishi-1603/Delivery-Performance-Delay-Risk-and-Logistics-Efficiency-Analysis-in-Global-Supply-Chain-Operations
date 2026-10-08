-- ============================================================
--  kpis.sql — the 5 official KPIs (SQLite & PostgreSQL compatible).
--  Every query mirrors src/kpis.py exactly; parity is enforced
--  by tests/test_kpis.py (Python) and documented in
--  docs/kpi_dictionary.md. Load data/processed/apl_clean.csv
--  into the shipments table first (schema.sql).
-- ============================================================

-- ── KPI 1: On-Time Delivery Rate ─────────────────────────────
-- Primary: delivered no later than scheduled (On-time + Early).
-- Strict variant (== scheduled) reported alongside.
-- Basis: all shipments (official). Add: WHERE NOT is_canceled
-- for the delivered-only sensitivity view.

SELECT
    COUNT(*)                                                    AS shipments,
    SUM(CASE WHEN delivery_delay_gap < 0 THEN 1 ELSE 0 END)     AS early,
    SUM(CASE WHEN delivery_delay_gap = 0 THEN 1 ELSE 0 END)     AS on_time,
    SUM(CASE WHEN delivery_delay_gap > 0 THEN 1 ELSE 0 END)     AS delayed,
    ROUND(100.0 * SUM(CASE WHEN delivery_delay_gap <= 0 THEN 1 ELSE 0 END) / COUNT(*), 2)
                                                                AS on_time_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN delivery_delay_gap = 0 THEN 1 ELSE 0 END) / COUNT(*), 2)
                                                                AS on_time_rate_strict_pct,
    ROUND(100.0 * SUM(CASE WHEN delivery_delay_gap > 0 THEN 1 ELSE 0 END) / COUNT(*), 2)
                                                                AS delayed_pct
FROM shipments;


-- ── KPI 2: Average Delivery Delay ────────────────────────────
-- Official: mean gap across ALL shipments (early NOT clipped to 0).
-- Supporting: median, p90, and mean delay among delayed only.

SELECT
    ROUND(AVG(delivery_delay_gap), 3)                           AS avg_gap_days,
    (SELECT ROUND(AVG(g), 1) FROM (
        SELECT delivery_delay_gap AS g FROM shipments
        ORDER BY delivery_delay_gap
        LIMIT 2 - (SELECT COUNT(*) FROM shipments) % 2
        OFFSET (SELECT (COUNT(*) - 1) / 2 FROM shipments)
    ))                                                          AS median_gap_days,
    -- nearest-rank P90 (gap values are small integers; equals the
    -- interpolated percentile on this dataset — verified vs pandas)
    (SELECT g FROM (
        SELECT delivery_delay_gap AS g FROM shipments
        ORDER BY delivery_delay_gap
        LIMIT 1
        OFFSET (SELECT CAST(0.9 * COUNT(*) AS INTEGER) FROM shipments)
    ))                                                          AS p90_gap_days,
    ROUND(AVG(CASE WHEN delivery_delay_gap > 0 THEN delivery_delay_gap END), 3)
                                                                AS avg_delay_when_delayed_days
FROM shipments;


-- ── KPI 3: Late Delivery Risk Ratio ──────────────────────────
-- The dataset's own flag (0/1) — deliberately distinct from KPI 1.

SELECT
    COUNT(*)                                          AS shipments,
    SUM("Late_delivery_risk")                           AS risk_1,
    ROUND(100.0 * SUM("Late_delivery_risk") / COUNT(*), 2) AS risk_ratio_pct
FROM shipments;


-- ── KPI 4: Shipping Mode Efficiency ──────────────────────────
-- Efficiency Index = 100% − delayed% (transparent, no arbitrary weights).

SELECT
    "Shipping Mode",
    COUNT(*)                                                    AS volume,
    SUM(CASE WHEN delivery_delay_gap > 0 THEN 1 ELSE 0 END)     AS delayed,
    ROUND(AVG(delivery_delay_gap), 3)                            AS avg_gap_days,
    ROUND(AVG(CASE WHEN delivery_delay_gap > 0 THEN delivery_delay_gap END), 2)
                                                                AS avg_delay_when_delayed_days,
    ROUND(100.0 * AVG("Late_delivery_risk"), 2)                    AS risk_ratio_pct,
    ROUND(SUM("Sales"), 0)                                         AS sales_exposure,
    ROUND(100.0 * SUM(CASE WHEN delivery_delay_gap > 0 THEN 1 ELSE 0 END) / COUNT(*), 2)
                                                                AS delayed_pct,
    ROUND(100.0 * SUM(CASE WHEN delivery_delay_gap <= 0 THEN 1 ELSE 0 END) / COUNT(*), 2)
                                                                AS efficiency_index_pct
FROM shipments
GROUP BY "Shipping Mode"
ORDER BY volume DESC;


-- ── KPI 5: Regional Delay Index ──────────────────────────────
-- Index = delayed share. ALWAYS read with volume + delayed count
-- (a 90% delay rate on 10 shipments is not a network problem).

SELECT
    "Order Region",
    COUNT(*)                                                    AS volume,
    SUM(CASE WHEN delivery_delay_gap > 0 THEN 1 ELSE 0 END)     AS delayed,
    ROUND(100.0 * SUM(CASE WHEN delivery_delay_gap > 0 THEN 1 ELSE 0 END) / COUNT(*), 2)
                                                                AS delayed_pct,
    ROUND(AVG(delivery_delay_gap), 3)                            AS avg_gap_days,
    ROUND(100.0 * AVG("Late_delivery_risk"), 2)                    AS risk_ratio_pct
FROM shipments
GROUP BY "Order Region"
ORDER BY delayed_pct DESC;