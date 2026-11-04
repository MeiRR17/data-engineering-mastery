#!/usr/bin/env bash
set -euo pipefail
command -v supabase >/dev/null || { echo 'Install the Supabase CLI first.' >&2; exit 1; }
supabase migration new --help >/dev/null
# Use the installed CLI to generate the timestamped migration filename.
supabase migration new datapulse_initial_schema
migration="$(find supabase/migrations -maxdepth 1 -type f -name '*_datapulse_initial_schema.sql' | sort | tail -n 1)"
test -n "$migration" || { echo 'Migration was not generated' >&2; exit 1; }
cp database/001_init.sql "$migration"
echo "Created $migration"
