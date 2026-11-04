-- Every seed event maps to exactly one fact (no fan-out and no losses).
with counted as (
    select s.event_id, count(f.event_id) as fact_rows
    from {{ ref('stg_events') }} s
    left join {{ ref('fct_earthquakes') }} f using(event_id)
    group by s.event_id
)
select * from counted where fact_rows <> 1
