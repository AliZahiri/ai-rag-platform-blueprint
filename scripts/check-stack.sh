#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-compose/docker-compose.yml}"
ENV_FILE="${ENV_FILE:-.env}"
STRICT="${STRICT:-false}"
LITELLM_PREFLIGHT_CONFIG="${LITELLM_PREFLIGHT_CONFIG:-configs/litellm-routes.example.json}"
READINESS_TIMEOUT_SECONDS="${READINESS_TIMEOUT_SECONDS:-3}"
LITELLM_READINESS_URL="${LITELLM_READINESS_URL:-}"

case "$STRICT" in
  true|false) ;;
  *)
    echo "STRICT must be either true or false; received: $STRICT" >&2
    exit 2
    ;;
esac

CHECKS=(
  "litellm-config=${LITELLM_PREFLIGHT_CONFIG}"
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

run_litellm_preflight() {
  python3 scripts/litellm_preflight.py --config "$LITELLM_PREFLIGHT_CONFIG"
}

if [[ "${1:-}" == "--plan" ]]; then
  print_checks
  exit 0
fi

run_litellm_preflight

docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps

collector_args=(
  python3 scripts/collect_platform_readiness.py
  --vector-db-url "http://localhost:${VECTOR_DB_PORT:-6333}"
  --prometheus-url "http://localhost:${PROMETHEUS_PORT:-9090}"
  --grafana-url "http://localhost:${GRAFANA_PORT:-3000}"
  --timeout-seconds "$READINESS_TIMEOUT_SECONDS"
)

if [[ -n "$LITELLM_READINESS_URL" ]]; then
  collector_args+=(--litellm-url "$LITELLM_READINESS_URL")
fi

if [[ "$STRICT" == "true" ]]; then
  collector_args+=(--require-ready)
fi

echo
echo "Platform readiness:"
"${collector_args[@]}"
