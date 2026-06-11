#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-compose/docker-compose.yml}"
ENV_FILE="${ENV_FILE:-.env}"

docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps

echo
echo "Suggested checks:"
echo "  curl http://localhost:${VECTOR_DB_PORT:-6333}/healthz"
echo "  curl http://localhost:${PROMETHEUS_PORT:-9090}/-/ready"
echo "  curl http://localhost:${GRAFANA_PORT:-3000}/api/health"
