-- Mart: one row per product with lifetime sales.

select
    product_id,
    max(product_name) as product_name,
    max(category) as category,
    sum(quantity) as total_quantity,
    sum(line_total) as total_revenue
from {{ ref('stg_orders') }}
group by product_id
