-- Materialized metric by UTC day and historically valid region.
select
    f.day_utc,
    r.region_name,
    count(*)::bigint as total_events,
    count(f.magnitude)::bigint as known_magnitude_events,
    round(avg(f.magnitude), 2) as avg_magnitude
from {{ ref('fct_earthquakes') }} f
join {{ ref('stg_regions') }} r on f.region_version_key = r.region_version_key
group by f.day_utc, r.region_name
