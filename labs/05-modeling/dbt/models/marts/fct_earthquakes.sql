-- Fact grain: exactly one row per event_id; valid-time join selects SCD2 region version.
select
    e.event_id,
    e.observed_at,
    cast(timezone('UTC', e.observed_at) as date) as day_utc,
    d.region_version_key,
    e.magnitude,
    e.source_updated_at
from {{ ref('stg_events') }} e
join {{ ref('stg_regions') }} d
  on e.region_code = d.region_code
 and e.observed_at >= d.valid_from
 and (d.valid_to is null or e.observed_at < d.valid_to)
