-- Type 2 windows belonging to the same business key must not overlap.
select a.region_code, a.region_version_key, b.region_version_key as conflicting_version
from {{ ref('stg_regions') }} a
join {{ ref('stg_regions') }} b
  on a.region_code=b.region_code
 and a.valid_from < b.valid_from
 and tstzrange(a.valid_from,coalesce(a.valid_to,'infinity'::timestamptz),'[)')
     && tstzrange(b.valid_from,coalesce(b.valid_to,'infinity'::timestamptz),'[)')
