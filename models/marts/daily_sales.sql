-- Mart: daily sales summary for dashboards.

select
    order_date,
    count(distinct order_id) as orders_count,
    sum(quantity) as items_sold,
    sum(line_total) as total_revenue
from {{ ref('stg_orders') }}
where status in ('completed', 'shipped')
group by order_date
