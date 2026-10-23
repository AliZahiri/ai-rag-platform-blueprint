# Operations Notes

## Health Checks

At minimum, monitor:

- Gateway availability and upstream errors
- RAG API health and worker queue health
- LLM router health
- Inference backend health and GPU memory usage
- PostgreSQL connections and replication or backup status
- Redis availability and memory pressure
- Vector database query latency

## Stack Readiness Verification

Run the local stack verifier after Compose starts:

```bash
STRICT=true ./scripts/check-stack.sh
```

`STRICT=true` makes every configured endpoint check a release-blocking
condition. The verifier uses the standard-library readiness collector and emits
a structured JSON report rather than relying on a local `curl` binary. Use the
default `STRICT=false` only for diagnostic runs where unavailable endpoints are
informational. See [platform readiness](platform-readiness.md) for the report
contract and optional LiteLLM probe.

## Observability

Recommended baseline:

- Prometheus for metrics
- Grafana for dashboards
- Alertmanager for alert routing
- Loki or ELK for logs
- Node Exporter for host metrics
- NVIDIA DCGM Exporter for GPU nodes
- Blackbox Exporter for endpoint checks

## Backup Targets

- PostgreSQL database
- Vector database collections
- Uploaded files and parsed documents
- Prompt/workflow configuration
- Gateway and router configuration
- Model cache metadata

## Incident Notes

Common failure modes:

- Model backend out of memory
- Vector DB slow queries
- Gateway timeout too short for LLM streaming
- Worker queue backlog
- Missing model cache on a new GPU node
- Prompt or retrieval configuration drift
