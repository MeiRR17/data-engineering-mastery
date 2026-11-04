-- Instructor-only reference. Learners should attempt starter.sql first.
-- Fact grain: exactly one row for every source event_id (not one per region version).
insert into analytics.fact_earthquake
  (event_id, observed_at, day_utc, region_sk, magnitude, source_updated_at)
select
  e.event_id,
  e.observed_at,
  (e.observed_at at time zone 'UTC')::date,
  d.region_sk,
  e.magnitude,
  e.source_updated_at
from public.earthquakes e
join analytics.event_region_map m on m.event_id = e.event_id
join analytics.dim_region d
  on d.region_code = m.region_code
 and e.observed_at >= d.valid_from
 and (d.valid_to is null or e.observed_at < d.valid_to)
on conflict (event_id) do update set
  observed_at = excluded.observed_at,
  day_utc = excluded.day_utc,
  region_sk = excluded.region_sk,
  magnitude = excluded.magnitude,
  source_updated_at = excluded.source_updated_at,
  loaded_at = now()
where (analytics.fact_earthquake.observed_at,
       analytics.fact_earthquake.day_utc,
       analytics.fact_earthquake.region_sk,
       analytics.fact_earthquake.magnitude,
       analytics.fact_earthquake.source_updated_at)
  is distinct from
      (excluded.observed_at, excluded.day_utc, excluded.region_sk,
       excluded.magnitude, excluded.source_updated_at);

create or replace view analytics.daily_region_metrics with (security_invoker = true) as
select
  f.day_utc,
  d.region_name,
  count(*)::bigint as total_events,
  count(f.magnitude)::bigint as known_magnitude_events,
  round(avg(f.magnitude),2) as avg_magnitude
from analytics.fact_earthquake f
join analytics.dim_region d on d.region_sk = f.region_sk
group by f.day_utc, d.region_name;

-- Even though this schema is private, enforce least privilege explicitly.
revoke all on analytics.daily_region_metrics from public, anon, authenticated;

