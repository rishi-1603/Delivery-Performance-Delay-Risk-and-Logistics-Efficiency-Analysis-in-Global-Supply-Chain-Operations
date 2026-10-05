-- ============================================================
--  analysis.sql — diagnostic queries (mirror src/analytics.py).
--  Verified results are in reports/analysis_report.md.
-- ============================================================

-- ── Risk flag vs calculated classification (KEY FINDING) ──────
-- Every disagreement is a canceled shipment.

SELECT
    SUM(CASE WHEN delivery_delay_gap > 0 AND late_delivery_risk = 1 THEN 1 ELSE 0 END) AS both_delayed_and_risk1,
    SUM(CASE WHEN delivery_delay_gap > 0 AND late_delivery_risk = 0 THEN 1 ELSE 0 END) AS delayed_but_risk0,
    (SELECT COUNT(*) FROM shipments WHERE late_delivery_risk = 1)
        = (SELECT COUNT(*) FROM shipments WHERE delivery_status = 'Late delivery')
                                                                                       AS risk1_equals_late_status
FROM shipments;

-- Status breakdown of the disagreements (expected: all 'Shipping canceled')
SELECT delivery_status, COUNT(*) AS delayed_but_risk0_rows
FROM shipments
WHERE delivery_delay_gap > 0 AND late_delivery_risk = 0
GROUP BY delivery_status;


-- ── Delivery gap distribution ─────────────────────────────────

SELECT delivery_delay_gap AS gap_days, COUNT(*) AS shipments,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM shipments
GROUP BY delivery_delay_gap
ORDER BY gap_days;


-- ── Market analysis ───────────────────────────────────────────

SELECT market,
       COUNT(*)                                                    AS volume,
       ROUND(100.0 * SUM(CASE WHEN delivery_delay_gap > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS delayed_pct,
       ROUND(100.0 * AVG(late_delivery_risk), 2)                    AS risk_ratio_pct,
       ROUND(SUM(sales), 0)                                         AS sales
FROM shipments
GROUP BY market
ORDER BY delayed_pct DESC;


-- ── Customer segment analysis ─────────────────────────────────

SELECT customer_segment,
       COUNT(*)                                                     AS volume,
       ROUND(100.0 * SUM(CASE WHEN delivery_delay_gap > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS delayed_pct,
       ROUND(100.0 * AVG(late_delivery_risk), 2)                     AS risk_ratio_pct,
       ROUND(AVG(order_profit_per_order), 2)                         AS avg_profit_per_order
FROM shipments
GROUP BY customer_segment
ORDER BY volume DESC;


-- ── Delayed % by market x shipping mode ───────────────────────
-- Shows whether the mode pattern is global (it is: First Class = 100%
-- delayed in every market) or regional.

SELECT market, shipping_mode,
       ROUND(100.0 * SUM(CASE WHEN delivery_delay_gap > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS delayed_pct
FROM shipments
GROUP BY market, shipping_mode
ORDER BY market, shipping_mode;


-- ── Financial exposure (associated value, NOT confirmed loss) ─

SELECT
    ROUND(SUM(sales), 0)                                            AS total_sales,
    ROUND(SUM(CASE WHEN delivery_delay_gap > 0 THEN sales END), 0)  AS delayed_sales,
    ROUND(100.0 * SUM(CASE WHEN delivery_delay_gap > 0 THEN sales END) / SUM(sales), 2) AS delayed_sales_pct,
    ROUND(SUM(order_profit_per_order), 0)                            AS total_profit,
    ROUND(SUM(CASE WHEN delivery_delay_gap > 0 THEN order_profit_per_order END), 0)   AS delayed_profit
FROM shipments;


-- ── Top regions by delayed count (volume-aware view) ──────────

SELECT order_region,
       COUNT(*) AS volume,
       SUM(CASE WHEN delivery_delay_gap > 0 THEN 1 ELSE 0 END) AS delayed,
       ROUND(100.0 * SUM(CASE WHEN delivery_delay_gap > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS delayed_pct
FROM shipments
GROUP BY order_region
ORDER BY delayed DESC
LIMIT 10;
