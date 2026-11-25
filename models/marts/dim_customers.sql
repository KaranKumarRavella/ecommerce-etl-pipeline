-- Mart: one row per customer with lifetime order history.

select
    customer_id,
    max(customer_name) as customer_name,
    max(customer_email) as customer_email,
    min(order_date) as first_order_date,
    max(order_date) as last_order_date,
    count(distinct order_id) as total_orders,
    sum(line_total) as total_spent
from {{ ref('stg_orders') }}
group by customer_id
