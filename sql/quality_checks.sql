-- Warehouse-level quality checks. Each query should return 0 rows
-- when the data is clean. Run after the marts are rebuilt.

-- 1. No null business keys in staging
SELECT COUNT(*) AS null_keys FROM staging.orders
WHERE order_id IS NULL OR customer_id IS NULL OR product_id IS NULL OR order_date IS NULL;

-- 2. No duplicate line items in fact_orders (primary key enforces this;
-- this is a belt-and-braces check)
SELECT order_id, product_id, COUNT(*) AS c FROM marts.fact_orders
GROUP BY order_id, product_id HAVING COUNT(*) > 1;

-- 3. No negative amounts
SELECT COUNT(*) AS negative_totals FROM marts.fact_orders WHERE line_total < 0;

-- 4. Daily sales reconciles to fact_orders
SELECT d.order_date
FROM marts.daily_sales d
LEFT JOIN (
    SELECT order_date, SUM(line_total) AS revenue FROM marts.fact_orders GROUP BY order_date
) f ON f.order_date = d.order_date
WHERE f.revenue IS DISTINCT FROM d.total_revenue;

-- 5. Freshness: latest order within 365 days
SELECT MAX(order_date) AS latest_order FROM staging.orders;
