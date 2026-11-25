-- Staging model: one row per order line, typed and lightly cleaned.
-- Source: staging.orders (loaded by the Python loader).

select
    order_id,
    order_date,
    customer_id,
    lower(trim(customer_email)) as customer_email,
    product_id,
    quantity,
    unit_price,
    quantity * unit_price as line_total,
    lower(trim(status)) as status,
    initcap(trim(region)) as region,
    currency
from {{ source('staging', 'orders') }}
where quantity > 0
  and unit_price >= 0
