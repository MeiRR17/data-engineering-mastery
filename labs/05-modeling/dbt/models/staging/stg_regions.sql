select
    cast(region_code as text) as region_code,
    cast(region_name as text) as region_name,
    cast(valid_from as timestamptz) as valid_from,
    cast(nullif(cast(valid_to as text), '') as timestamptz) as valid_to,
    cast(region_code as text) || '|' || cast(valid_from as text) as region_version_key
from {{ ref('regions') }}
