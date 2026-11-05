-- Fixed synthetic fixture oracles (not for real production datasets).
select 'old-version' as broken_check
where (select r.region_name from {{ ref('fct_earthquakes') }} f
      join {{ ref('stg_regions') }} r using (region_version_key)
      where f.event_id='lab-b') is distinct from 'East Sector'
union all
select 'new-version'
where (select r.region_name from {{ ref('fct_earthquakes') }} f
      join {{ ref('stg_regions') }} r using (region_version_key)
      where f.event_id='lab-c') is distinct from 'East District'
union all
select 'all-null-mean'
where (select avg_magnitude from {{ ref('daily_region_metrics') }}
       where region_name='West Sector') is not null
union all
select 'expected-source-count'
where (select count(*) from {{ ref('fct_earthquakes') }}) <> 4
