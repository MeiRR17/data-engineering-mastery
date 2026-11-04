do $replay$
declare
  v_total bigint;
  v_avg numeric;
begin
  select count(*) into v_total from analytics.fact_earthquake;
  if v_total <> 4 then raise exception 'rebuild duplicated facts: %', v_total; end if;
  if (select magnitude from analytics.fact_earthquake where event_id='lab-b') <> 4.40 then
    raise exception 'upstream correction did not refresh existing fact';
  end if;
  if (select source_updated_at from analytics.fact_earthquake where event_id='lab-b') <>
     '2026-01-03T11:10:00Z'::timestamptz then
    raise exception 'lineage/source update timestamp out of sync';
  end if;
  select avg_magnitude into v_avg from analytics.daily_region_metrics
    where day_utc='2026-01-01' and region_name='East Sector';
  if v_avg <> 4.40 then
    raise exception 'mart did not recompute updated metric: %', v_avg;
  end if;
  if (select sum(total_events) from analytics.daily_region_metrics) <> 4 then
    raise exception 'mart double-counted after replay';
  end if;
end
$replay$;

