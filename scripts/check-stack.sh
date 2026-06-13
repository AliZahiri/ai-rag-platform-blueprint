#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-compose/docker-compose.yml}"
ENV_FILE="${ENV_FILE:-.env}"
STRICT="${STRICT:-false}"

CHECKS=(
  "vector-db=http://localhost:${VECTOR_DB_PORT:-6333}/healthz"
  "prometheus=http://localhost:${PROMETHEUS_PORT:-9090}/-/ready"
  "grafana=http://localhost:${GRAFANA_PORT:-3000}/api/health"
)

print_checks() {
  for item in "${CHECKS[@]}"; do
    name="${item%%=*}"
    url="${item#*=}"
    printf '%-12s %s\n' "$name" "$url"
  done
}

if [[ "${1:-}" == "--plan" ]]; then
  print_checks
  exit 0
fi

docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps

echo
echo "Endpoint checks:"

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is not available; suggested checks:"
  print_checks
  exit 0
fi

failed=0
for item in "${CHECKS[@]}"; do
  name="${item%%=*}"
  url="${item#*=}"
  if curl --fail --silent --show-error --max-time 3 "$url" >/dev/null; then
    printf '  [ok]   %s\n' "$name"
  else
    printf '  [fail] %s -> %s\n' "$name" "$url"
    failed=1
  fi
done

if [[ "$STRICT" == "true" && "$failed" -ne 0 ]]; then
  exit 1
fi
