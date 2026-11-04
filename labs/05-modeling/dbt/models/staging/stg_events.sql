select
    cast(event_id as text) as event_id,
    cast(observed_at as timestamptz) as observed_at,
    cast(source_updated_at as timestamptz) as source_updated_at,
    cast(region_code as text) as region_code,
    cast(magnitude as numeric) as magnitude
from {{ ref('events') }}
