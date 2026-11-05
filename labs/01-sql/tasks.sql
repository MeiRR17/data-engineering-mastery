-- Write one SELECT or WITH query for each task, in the designated block.
-- task: duplicates
SELECT 'TODO' AS event_id, 0 AS versions;

-- task: latest
SELECT 'TODO' AS event_id, 'TODO' AS location, '1970-01-01' AS occurred_on,
       NULL AS magnitude, '1970-01-01T00:00:00Z' AS updated_at;

-- task: daily
SELECT '1970-01-01' AS occurred_on, 0 AS event_count, NULL AS avg_magnitude;

-- task: strongest
SELECT 'TODO' AS location, 'TODO' AS event_id, 0.0 AS magnitude;
