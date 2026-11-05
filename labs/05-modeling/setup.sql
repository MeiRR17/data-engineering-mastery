-- Disposable PostgreSQL 17 lab only. NOT a migration for cloud Supabase.
-- A star schema has one fact row per source event and a history-aware region dimension.
create extension if not exists btree_gist;
create schema analytics;
revoke all on schema analytics from public, anon, authenticated;

create table analytics.dim_region (
  region_sk bigint generated always as identity primary key,
  region_code text not null,
  region_name text not null check (length(trim(region_name)) > 0),
  valid_from timestamptz not null,
  valid_to timestamptz,
  constraint region_range_valid check (valid_to is null or valid_to > valid_from),
  constraint region_code_start_unique unique (region_code, valid_from),
  constraint no_overlapping_region_versions exclude using gist
    (region_code with =,
     tstzrange(valid_from, coalesce(valid_to, 'infinity'::timestamptz), '[)') with &&)
);

-- Same business key E has two successive (nonoverlapping) versions.
-- This is a small Type 2 slowly changing dimension, not a Type 1 overwrite.
insert into analytics.dim_region(region_code, region_name, valid_from, valid_to) values
 ('N','North Ridge', '2025-01-01T00:00:00Z', null),
 ('E','East Sector', '2025-01-01T00:00:00Z', '2026-01-02T00:00:00Z'),
 ('E','East District', '2026-01-02T00:00:00Z', null),
 ('W','West Sector', '2025-01-01T00:00:00Z', null);

-- Each event has one region classification. Stable natural grain: event_id.
create table analytics.event_region_map (
  event_id text primary key references public.earthquakes(event_id),
  region_code text not null
);
insert into analytics.event_region_map(event_id, region_code) values
 ('lab-a','N'), ('lab-b','E'), ('lab-c','E'), ('lab-d','W');

create table analytics.fact_earthquake (
  event_id text primary key references public.earthquakes(event_id),
  observed_at timestamptz not null,
  day_utc date not null,
  region_sk bigint not null references analytics.dim_region(region_sk),
  magnitude numeric(5,2),
  source_updated_at timestamptz not null,
  loaded_at timestamptz not null default now(),
  constraint fact_magnitude_valid check (magnitude is null or magnitude between -5 and 12)
);
create index on analytics.fact_earthquake(day_utc, region_sk);

-- analytics is deliberately not an exposed Supabase Data API schema.
revoke all on all tables in schema analytics from public, anon, authenticated;

