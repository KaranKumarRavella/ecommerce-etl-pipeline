-- Plain-Postgres rebuild of the marts from staging.orders.
-- This mirrors models/marts/*.sql, which use dbt ref() syntax and are
-- intended for a dbt run. The Python loader runs this file instead.

TRUNCATE TABLE marts.dim_customers;
INSERT INTO marts.dim_customers
    (customer_id, customer_name, customer_email, first_order_date,
     last_order_date, total_orders, total_spent)
SELECT
    customer_id,
    max(customer_name),
    max(customer_email),
    min(order_date),
    max(order_date),
    count(distinct order_id),
    sum(line_total)
FROM staging.orders
GROUP BY customer_id;

TRUNCATE TABLE marts.dim_products;
INSERT INTO marts.dim_products
    (product_id, product_name, category, total_quantity, total_revenue)
SELECT
    product_id,
    max(product_name),
    max(category),
    sum(quantity),
    sum(line_total)
FROM staging.orders
GROUP BY product_id;

TRUNCATE TABLE marts.fact_orders;
INSERT INTO marts.fact_orders
    (order_id, order_date, customer_id, product_id, quantity,
     unit_price, line_total, status, region)
SELECT order_id, order_date, customer_id, product_id, quantity,
       unit_price, line_total, status, region
FROM staging.orders;

TRUNCATE TABLE marts.daily_sales;
INSERT INTO marts.daily_sales
    (order_date, orders_count, items_sold, total_revenue)
SELECT
    order_date,
    count(distinct order_id),
    sum(quantity),
    sum(line_total)
FROM staging.orders
WHERE status IN ('completed', 'shipped')
GROUP BY order_date;
