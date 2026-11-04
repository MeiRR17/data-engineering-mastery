-- task: duplicates
SELECT event_id, COUNT(*) AS versions
FROM quake_events GROUP BY event_id HAVING COUNT(*) > 1;

-- task: latest
WITH ranked AS (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY event_id ORDER BY updated_at DESC, row_id DESC
    ) AS position
    FROM quake_events
)
SELECT event_id, location, occurred_on, magnitude, updated_at
FROM ranked WHERE position = 1;

-- task: daily
WITH ranked AS (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY event_id ORDER BY updated_at DESC, row_id DESC
    ) AS position
    FROM quake_events
)
SELECT occurred_on, COUNT(*) AS event_count, ROUND(AVG(magnitude), 3) AS avg_magnitude
FROM ranked WHERE position = 1 GROUP BY occurred_on;

-- task: strongest
WITH canonical AS (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY event_id ORDER BY updated_at DESC, row_id DESC
    ) AS position
    FROM quake_events
), ranked AS (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY location ORDER BY magnitude DESC, event_id ASC
    ) AS loc_position
    FROM canonical WHERE position = 1 AND magnitude IS NOT NULL
)
SELECT location, event_id, magnitude FROM ranked WHERE loc_position = 1;
