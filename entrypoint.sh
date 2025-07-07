#!/bin/bash

echo "Running Alembic migrations..."
uv run alembic -c resources/migrations/alembic.ini upgrade head

echo "Starting the app..."
exec uv run uvicorn main:app --host 0.0.0.0 --port 8001
