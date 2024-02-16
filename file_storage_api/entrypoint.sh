#!/bin/sh
# Use a SQL query to check if the alembic_version table exists and store the result
TABLE_EXISTS=$(PGPASSWORD=$AUTH_POSTGRES_PASSWORD psql -h $FILE_STORAGE_POSTGRES_HOST -p $FILE_STORAGE_POSTGRES_PORT -U $FILE_STORAGE_POSTGRES_USER -d $FILE_STORAGE_POSTGRES_DB -tAc "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version');" 2>/dev/null)

if [ "$TABLE_EXISTS" = 't' ]; then
    echo "Migrations have already been applied"
else
    echo "Running migrations"
    alembic revision --autogenerate -m "Create tables for file storage service"
    alembic upgrade head
fi

exec uvicorn src.main:app --host 0.0.0.0 --port 8080
