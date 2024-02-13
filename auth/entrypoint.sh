#!/bin/sh
# Use a SQL query to check if the alembic_version table exists and store the result
TABLE_EXISTS=$(PGPASSWORD=$AUTH_POSTGRES_PASSWORD psql -h $AUTH_POSTGRES_HOST -p $AUTH_POSTGRES_PORT -U $AUTH_POSTGRES_USER -d $AUTH_POSTGRES_DB -tAc "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version');" 2>/dev/null)

if [ "$TABLE_EXISTS" = 't' ]; then
    echo "Migrations have already been applied"
else
    echo "Running migrations"
    alembic revision --autogenerate -m "Create tables for auth service"
    alembic upgrade head
fi

exec uvicorn src.main:app --host 0.0.0.0 --port 8000
