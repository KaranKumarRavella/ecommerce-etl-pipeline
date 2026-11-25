-- Staging model: distinct customers as seen in orders.

select distinct
    customer_id,
    trim(customer_name) as customer_name,
    lower(trim(customer_email)) as customer_email
from {{ source('staging', 'orders') }}
