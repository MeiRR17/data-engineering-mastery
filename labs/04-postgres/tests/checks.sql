-- Stage 04 integration assertions run after the canonical schema, fixture and learner SQL.
do $$
begin
 if (select count(*) from public.raw_earthquakes) <> 4 then raise exception 'raw ingestion count'; end if;
 if (select count(*) from public.earthquakes) <> 4 then raise exception 'curated ingestion count'; end if;
 if (select total_events from public.daily_stats where day='2026-01-01') <> 2
 then raise exception 'incorrect UTC daily aggregation'; end if;
 if has_table_privilege('anon','public.raw_earthquakes','SELECT')
 then raise exception 'anon may read raw data'; end if;
 if has_table_privilege('anon','public.ingest_runs','SELECT')
 then raise exception 'anon may read operational logs'; end if;
 if has_table_privilege('anon','public.earthquakes','INSERT')
 then raise exception 'anon may write curated data'; end if;
 if has_function_privilege('anon','public.ingest_earthquake_batch(jsonb)','EXECUTE')
 then raise exception 'anon may invoke ingestion RPC'; end if;
 if not exists (select 1 from pg_class
     where oid='public.daily_stats'::regclass and 'security_invoker=true'=any(reloptions))
 then raise exception 'daily_stats view is not security_invoker'; end if;
 if not exists (select 1 from pg_class
     where oid='public.stage04_magnitude_summary'::regclass and 'security_invoker=true'=any(reloptions))
 then raise exception 'learner view is not security_invoker'; end if;
 if not has_table_privilege('anon','public.stage04_magnitude_summary','SELECT')
 then raise exception 'anon must read learner summary'; end if;
 if has_table_privilege('authenticated','public.stage04_magnitude_summary','SELECT')
 then raise exception 'unexpected authenticated access'; end if;
 if (select count(*) from public.stage04_magnitude_summary) <> 4
 then raise exception 'expected four magnitude groups'; end if;
 if exists (
   select 1 from
     (values ('minor',1::bigint),('moderate',1::bigint),
             ('strong',1::bigint),('unknown',1::bigint)) expected(band,total_events)
   full outer join public.stage04_magnitude_summary actual using(band,total_events)
   where expected.band is null or actual.band is null
 ) then raise exception 'incorrect magnitude aggregation'; end if;
end $$;

-- Verify actual role behavior, rather than merely checking a grant catalog.
set role anon;
do $$
declare total bigint;
begin
 select count(*) into total from public.daily_stats;
 if total <> 2 then raise exception 'anon cannot read daily statistics'; end if;
 select sum(total_events) into total from public.stage04_magnitude_summary;
 if total <> 4 then raise exception 'anon cannot read learner view'; end if;
 begin
  execute 'select count(*) from public.raw_earthquakes' into total;
  raise exception 'anon read restricted raw data';
 exception when insufficient_privilege then null;
 end;
 begin
  execute 'delete from public.earthquakes';
  raise exception 'anon deleted curated data';
 exception when insufficient_privilege then null;
 end;
 begin
  execute 'select public.ingest_earthquake_batch(''[]''::jsonb)' into total;
  raise exception 'anon invoked restricted RPC';
 exception when insufficient_privilege then null;
 end;
end $$;
reset role;

-- Re-running an identical batch must not duplicate records.
set role service_role;
select public.ingest_earthquake_batch(
 '[{"event_id":"lab-b","observed_at":"2026-01-01T11:00:00Z",
   "source_updated_at":"2026-01-01T11:10:00Z","magnitude":4.1,
   "place":"Synthetic East","longitude":35.3,"latitude":30.9,"depth_km":11,
   "source_url":"https://example.org/lab-b",
   "payload_sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
   "raw_payload":{"source":"synthetic","id":"lab-b"}}]'::jsonb);
reset role;
do $$ begin
 if (select count(*) from public.earthquakes) <> 4 then
  raise exception 'duplicate delivery caused fan-out'; end if;
end $$;

-- A stale source update must not overwrite fresher data.
set role service_role;
select public.ingest_earthquake_batch(
 '[{"event_id":"lab-b","observed_at":"2026-01-01T11:00:00Z",
   "source_updated_at":"2025-01-01T11:10:00Z","magnitude":9.0,
   "place":"Stale update","longitude":35.3,"latitude":30.9,"depth_km":11,
   "source_url":"https://example.org/lab-b",
   "payload_sha256":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
   "raw_payload":{"source":"synthetic","id":"lab-b-old"}}]'::jsonb);
reset role;
do $$ begin
 if (select magnitude from public.earthquakes where event_id='lab-b') <> 4.1 then
  raise exception 'stale source overwrote curated value'; end if;
 if (select payload_sha256 from public.raw_earthquakes where event_id='lab-b') <> repeat('b',64) then
  raise exception 'stale source overwrote raw value'; end if;
end $$;

-- A newer source update must take effect without adding a row.
set role service_role;
select public.ingest_earthquake_batch(
 '[{"event_id":"lab-b","observed_at":"2026-01-01T11:00:00Z",
   "source_updated_at":"2026-01-03T11:10:00Z","magnitude":4.4,
   "place":"Updated event","longitude":35.3,"latitude":30.9,"depth_km":11,
   "source_url":"https://example.org/lab-b",
   "payload_sha256":"ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
   "raw_payload":{"source":"synthetic","id":"lab-b-new"}}]'::jsonb);
reset role;
do $$ begin
 if (select magnitude from public.earthquakes where event_id='lab-b') <> 4.4 then
  raise exception 'newer source update missing'; end if;
 if (select count(*) from public.earthquakes) <> 4 then
  raise exception 'newer source update caused fan-out'; end if;
end $$;

-- A partial write must be rolled back on constraint violation.
set role service_role;
do $$ begin
 begin
  perform public.ingest_earthquake_batch(
   '[{"event_id":"lab-must-rollback","observed_at":"2026-01-03T01:00:00Z",
      "source_updated_at":"2026-01-03T01:05:00Z","magnitude":3,
      "place":"First valid row","longitude":35,"latitude":31,"depth_km":5,
      "source_url":"https://example.org/rollback",
      "payload_sha256":"1111111111111111111111111111111111111111111111111111111111111111",
      "raw_payload":{"source":"synthetic"}},
     {"event_id":"lab-invalid-coordinates","observed_at":"2026-01-03T02:00:00Z",
      "source_updated_at":"2026-01-03T02:05:00Z","magnitude":3,
      "place":"Invalid row","longitude":35,"latitude":999,"depth_km":5,
      "source_url":"https://example.org/invalid",
      "payload_sha256":"2222222222222222222222222222222222222222222222222222222222",
      "raw_payload":{"source":"synthetic"}}]'::jsonb);
  raise exception 'invalid batch unexpectedly succeeded';
 exception when check_violation then null;
 end;
end $$;
reset role;
do $$ begin
 if exists (select 1 from public.raw_earthquakes where event_id='lab-must-rollback') or
    exists (select 1 from public.earthquakes where event_id='lab-must-rollback')
 then raise exception 'atomic rollback failed'; end if;
end $$;
