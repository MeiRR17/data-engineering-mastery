-- Metrics must reconcile with fact counts, including known magnitudes.
with totals as (
 select
    (select count(*) from {{ ref('fct_earthquakes') }}) as fact_events,
    (select coalesce(sum(total_events),0) from {{ ref('daily_region_metrics') }}) as mart_events,
    (select count(magnitude) from {{ ref('fct_earthquakes') }}) as fact_known,
    (select coalesce(sum(known_magnitude_events),0) from {{ ref('daily_region_metrics') }}) as mart_known
)
select * from totals where fact_events <> mart_events or fact_known <> mart_known
