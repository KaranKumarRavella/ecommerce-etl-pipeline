-- Mart: cleaned order lines, the grain for reporting.

select
    order_id,
    order_date,
    customer_id,
    product_id,
    quantity,
    unit_price,
    line_total,
    status,
    region
from {{ ref('stg_orders') }}
