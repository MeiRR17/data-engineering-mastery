-- These assertions run against the learner's SQL, not a hand-picked result.
-- A faulty fact join, wrong grain, bad time boundary or AVG denominator must fail.
do $checks$
declare
  source_count bigint;
  fact_count bigint;
  bad_count bigint;
  mean numeric;
  last_version text;
  old_version text;
begin
  select count(*) into source_count from public.earthquakes;
  select count(*) into fact_count from analytics.fact_earthquake;
  if source_count <> 4 or fact_count <> source_count then
    raise exception 'fact grain/coverage mismatch: facts %, source %', fact_count, source_count;
  end if;

  select count(*) into bad_count
    from public.earthquakes e
    left join analytics.fact_earthquake f using(event_id)
    where f.event_id is null or f.observed_at <> e.observed_at
      or f.day_utc <> (e.observed_at at time zone 'UTC')::date
      or f.magnitude is distinct from e.magnitude;
  if bad_count <> 0 then
    raise exception 'fact event mapping, UTC conversion or measures incorrect';
  end if;

  select d.region_name into old_version
  from analytics.fact_earthquake f join analytics.dim_region d using(region_sk)
  where f.event_id = 'lab-b';
  select d.region_name into last_version
  from analytics.fact_earthquake f join analytics.dim_region d using(region_sk)
  where f.event_id = 'lab-c';
  if old_version is distinct from 'East Sector' or
     last_version is distinct from 'East District' then
    raise exception 'SCD2 as-of version mismatch: %, %', old_version, last_version;
  end if;

  if not exists (select 1 from pg_class
       where oid='analytics.daily_region_metrics'::regclass
         and 'security_invoker=true'=any(reloptions)) then
    raise exception 'mart view must use security_invoker';
  end if;
  if has_schema_privilege('anon','analytics','USAGE') or
     has_schema_privilege('authenticated','analytics','USAGE') then
    raise exception 'analytics private schema exposed';
  end if;
  if has_table_privilege('anon','analytics.fact_earthquake','SELECT') then
    raise exception 'anonymous user can read private fact table';
  end if;

  if (select count(*) from analytics.daily_region_metrics) <> 4 then
    raise exception 'unexpected daily-region group count or fan-out';
  end if;
  if (select sum(total_events) from analytics.daily_region_metrics) <> source_count then
    raise exception 'double count or missing metric rows';
  end if;
  if (select sum(known_magnitude_events) from analytics.daily_region_metrics) <> 3 then
    raise exception 'NULL magnitude incorrectly counted';
  end if;
  if (select total_events from analytics.daily_region_metrics
      where day_utc='2026-01-02' and region_name='West Sector') <> 1 then
    raise exception 'West region event count incorrect';
  end if;
  select avg_magnitude into mean from analytics.daily_region_metrics
    where day_utc='2026-01-02' and region_name='West Sector';
  if mean is not null then
    raise exception 'AVG for all-NULL magnitudes should be NULL, not zero';
  end if;
  select avg_magnitude into mean from analytics.daily_region_metrics
    where day_utc='2026-01-01' and region_name='East Sector';
  if mean <> 4.10 then
    raise exception 'initial East Sector average incorrect: %', mean;
  end if;

  -- An exclusion constraint must reject SCD2 intervals that overlap.
  begin
    insert into analytics.dim_region(region_code,region_name,valid_from,valid_to)
      values ('E','Overlap must fail','2026-01-01T12:00:00Z','2026-01-01T13:00:00Z');
    raise exception 'overlapping SCD2 interval was accepted';
  exception when exclusion_violation then
    null;
  end;
end
$checks$;

