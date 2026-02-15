#!/bin/bash
set -e
cd "$(dirname "$0")/.."

echo "Starting test infrastructure..."
docker compose -p coonspect_test --env-file ../.env.test -f ../docker-compose.test.yml up -d --force-recreate

echo "Waiting for MongoDB..."
sleep 3

echo "Running pytest..."
PYTHONPATH=. MONGO_HOST=localhost uv run pytest -v -s --cov=app --cov-report=html:htmlcov

echo "Cleaning up..."
docker compose -p coonspect_test --env-file ../.env.test -f ../docker-compose.test.yml down