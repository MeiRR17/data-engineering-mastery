-- Simulates one upstream correction INSIDE THE DISPOSABLE CONTAINER ONLY.
-- We test whether rerunning the mart rebuild updates a measure without fan-out.
update public.earthquakes
set magnitude=4.40, source_updated_at='2026-01-03T11:10:00Z'
where event_id='lab-b';

