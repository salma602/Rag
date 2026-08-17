#!/bin/bash
set -e

echo "Running database migrations..."

cd /app/models/db_schems/mini_rag/

alembic upgrade head

cd /app

echo "Starting FastAPI..."

exec "$@"