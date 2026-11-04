-- This reference exists solely to validate the learning assessment in CI.
create or replace view public.stage04_magnitude_summary
with (security_invoker = true)
as
select case when magnitude is null then 'unknown'
            when magnitude < 2 then 'minor'
            when magnitude < 5 then 'moderate'
            else 'strong' end::text as band,
       count(*)::bigint as total_events
from public.earthquakes
group by 1;
revoke all on public.stage04_magnitude_summary from public, anon, authenticated;
grant select on public.stage04_magnitude_summary to anon;
