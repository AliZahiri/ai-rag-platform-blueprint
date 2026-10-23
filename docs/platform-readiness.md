# Platform readiness collector

`scripts/collect_platform_readiness.py` performs bounded HTTP readiness probes
against the local platform services and writes a structured JSON report. It is
an operational probe, not a substitute for a retrieval-quality evaluation or a
model-provider health check.

By default it checks Qdrant, Prometheus, and Grafana. LiteLLM is checked only
when `--litellm-url` is supplied, so the default workflow remains provider-free
and works when the optional Compose `llm` profile is disabled.

```bash
python3 scripts/collect_platform_readiness.py \
  --vector-db-url http://localhost:6333 \
  --prometheus-url http://localhost:9090 \
  --grafana-url http://localhost:3000 \
  --require-ready
```

The report contains the platform decision (`ready` or `degraded`), the required
services, failed required services, timestamped observations, HTTP status, and
latency. It intentionally records only an error type for unavailable services;
response bodies, URLs with credentials, query parameters, and raw network error
text are never emitted.

For a Compose deployment that enables LiteLLM:

```bash
python3 scripts/collect_platform_readiness.py \
  --litellm-url http://localhost:4000 \
  --require-ready
```

`--require-ready` returns exit code `1` for a degraded platform and exit code
`2` for invalid collector input. Without it, the command remains a diagnostic
and exits successfully after emitting the report.

`scripts/check-stack.sh` calls the collector after Compose status and LiteLLM
configuration preflight. Set `STRICT=true` to make a degraded report block the
command. Use `LITELLM_READINESS_URL=http://localhost:4000` only when the
optional LiteLLM profile is running.
