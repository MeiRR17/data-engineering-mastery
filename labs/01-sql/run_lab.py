from pathlib import Path
import sqlite3

schema=Path(__file__).with_name('schema.sql').read_text(encoding='utf8')
db=sqlite3.connect(':memory:')
db.executescript(schema)
print('SQL detective: events data (synthetic), including a duplicate event_id')
for row in db.execute('select event_id, location, occurred_on, magnitude, updated_at from quake_events order by row_id'):
    print(row)
print('Your task: write duplicate detection, latest-update deduplication, daily summary queries.')
print('Why does AVG skip the NULL magnitude?')
