#!/bin/bash
# Start Mealie on Railway.
#  1. Listen on Railway's PORT (Mealie reads API_PORT).
#  2. Default to Postgres when POSTGRES_URL_OVERRIDE is set, else SQLite on the volume.
#  3. Run the database migrations, then replace Mealie's built-in first admin
#     (changeme@example.com / MyPassword) with MEALIE_ADMIN_EMAIL and
#     MEALIE_ADMIN_PASSWORD, so a fresh deploy never has a known login.
#  4. Hand over to upstream's own entrypoint.
set -e

export API_PORT="${PORT:-${API_PORT:-9000}}"
if [ -z "${DB_ENGINE:-}" ]; then
  if [ -n "${POSTGRES_URL_OVERRIDE:-}" ]; then export DB_ENGINE=postgres; else export DB_ENGINE=sqlite; fi
fi
export TZ="${TZ:-UTC}"

/opt/mealie/bin/python /railway/bootstrap_admin.py

exec /app/run.sh "$@"
