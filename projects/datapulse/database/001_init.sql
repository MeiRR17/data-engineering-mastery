-- DataPulse v0.1.0 — run against a fresh, dedicated Supabase project.
-- Educational, public-source dataset. No personally identifying data.
-- Safe from the browser: only curated earthquakes and daily_stats are exposed.

begin;

create table if not exists public.raw_earthquakes (
  event_id text primary key,
  raw_payload jsonb not null,
  payload_sha256 text not null check (length(payload_sha256) = 64),
  source_updated_at timestamptz not null,
  received_at timestamptz not null default now()
);

create table if not exists public.earthquakes (
  event_id text primary key,
  observed_at timestamptz not null,
  source_updated_at timestamptz not null,
  magnitude numeric(5,2),
  place text not null,
  longitude double precision not null check (longitude between -180 and 180),
  latitude double precision not null check (latitude between -90 and 90),
  depth_km numeric(8,2) not null check (depth_km between -50 and 1000),
  source_url text not null,
  payload_sha256 text not null check (length(payload_sha256) = 64),
  processed_at timestamptz not null default now(),
  constraint magnitude_reasonable check (magnitude is null or magnitude between -5 and 12)
);

create index if not exists earthquakes_observed_at_idx on public.earthquakes (observed_at desc);
create index if not exists earthquakes_magnitude_idx on public.earthquakes (magnitude desc) where magnitude is not null;

create table if not exists public.ingest_runs (
  run_id uuid primary key,
  feed_name text not null,
  status text not null check (status in ('running', 'success', 'failed')),
  source_rows integer not null default 0,
  valid_rows integer not null default 0,
  rejected_rows integer not null default 0,
  loaded_rows integer not null default 0,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  constraint ingest_nonnegative check (
    source_rows >= 0 and valid_rows >= 0 and rejected_rows >= 0 and loaded_rows >= 0
  )
);

-- Explicit permissions, not assumptions about the project's default grants.
alter table public.raw_earthquakes enable row level security;
alter table public.earthquakes enable row level security;
alter table public.ingest_runs enable row level security;

revoke all on public.raw_earthquakes from anon, authenticated;
revoke all on public.ingest_runs from anon, authenticated;
revoke all on public.earthquakes from anon, authenticated;

-- The public dashboard can read curated public data, but cannot mutate it.
grant select on public.earthquakes to anon;
drop policy if exists datapulse_public_curated_read on public.earthquakes;
create policy datapulse_public_curated_read on public.earthquakes
for select to anon using (true);

-- A read-only analytics view that executes with the caller's RLS permissions.
create or replace view public.daily_stats with (security_invoker = true) as
select
  (observed_at at time zone 'UTC')::date as day,
  count(*)::bigint as total_events,
  count(magnitude)::bigint as magnitude_count,
  avg(magnitude) as avg_magnitude,
  max(magnitude) as max_magnitude
from public.earthquakes
group by (observed_at at time zone 'UTC')::date;
revoke all on public.daily_stats from anon, authenticated;
grant select on public.daily_stats to anon;

-- Service-only, transactionally ingest both raw and normalized layers.
-- This function is deliberately SECURITY INVOKER, not DEFINER.
create or replace function public.ingest_earthquake_batch(p_rows jsonb)
returns integer
language plpgsql
security invoker
set search_path = ''
as $$
declare
  v_count integer;
begin
  if jsonb_typeof(p_rows) is distinct from 'array' then
    raise exception 'p_rows must be an array';
  end if;
  v_count := jsonb_array_length(p_rows);
  if v_count > 100 then
    raise exception 'maximum batch size is 100';
  end if;

  insert into public.raw_earthquakes (
    event_id, raw_payload, payload_sha256, source_updated_at
  )
  select r.event_id, r.raw_payload, r.payload_sha256, r.source_updated_at
  from jsonb_to_recordset(p_rows) as r(
    event_id text, observed_at timestamptz, source_updated_at timestamptz,
    magnitude numeric, place text, longitude double precision,
    latitude double precision, depth_km numeric, source_url text,
    payload_sha256 text, raw_payload jsonb
  )
  on conflict (event_id) do update
  set raw_payload = excluded.raw_payload,
      payload_sha256 = excluded.payload_sha256,
      source_updated_at = excluded.source_updated_at,
      received_at = now()
  where excluded.source_updated_at >= raw_earthquakes.source_updated_at
    and excluded.payload_sha256 is distinct from raw_earthquakes.payload_sha256;

  insert into public.earthquakes (
    event_id, observed_at, source_updated_at, magnitude, place,
    longitude, latitude, depth_km, source_url, payload_sha256
  )
  select r.event_id, r.observed_at, r.source_updated_at, r.magnitude, r.place,
         r.longitude, r.latitude, r.depth_km, r.source_url, r.payload_sha256
  from jsonb_to_recordset(p_rows) as r(
    event_id text, observed_at timestamptz, source_updated_at timestamptz,
    magnitude numeric, place text, longitude double precision,
    latitude double precision, depth_km numeric, source_url text,
    payload_sha256 text, raw_payload jsonb
  )
  on conflict (event_id) do update
  set observed_at = excluded.observed_at,
      source_updated_at = excluded.source_updated_at,
      magnitude = excluded.magnitude,
      place = excluded.place,
      longitude = excluded.longitude,
      latitude = excluded.latitude,
      depth_km = excluded.depth_km,
      source_url = excluded.source_url,
      payload_sha256 = excluded.payload_sha256,
      processed_at = now()
  where excluded.source_updated_at >= earthquakes.source_updated_at
    and excluded.payload_sha256 is distinct from earthquakes.payload_sha256;

  return v_count;
end;
$$;

-- Default EXECUTE privileges on functions are often PUBLIC. Close the route.
revoke all on function public.ingest_earthquake_batch(jsonb) from public, anon, authenticated;
grant execute on function public.ingest_earthquake_batch(jsonb) to service_role;
grant all on public.raw_earthquakes, public.earthquakes, public.ingest_runs to service_role;
grant select on public.daily_stats to service_role;

commit;
