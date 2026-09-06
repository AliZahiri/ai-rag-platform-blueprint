# LiteLLM Pre-Flight Validation

The LiteLLM layer should fail fast before it accepts real RAG traffic. The default validation path must stay free and local: it should validate configuration and environment requirements without making paid provider calls.

## Validation Scope

Run pre-flight validation before rollout, during CI, and whenever route configuration changes.

Required checks:

- every route alias resolves to a concrete provider and model
- the route list is not empty
- fallback routes reference defined aliases only
- fallback chains do not contain cycles
- per-route limits are present for RPM, TPM, retries, timeout, and cost cap
- required environment variable names are declared for each provider route
- optional secret presence checks fail loudly when enabled
- capabilities required by the RAG stack are available: streaming, tool calling, JSON mode, and enough context window
- observability fields are enabled for latency, token usage, cost, and failures

All route limits must be finite, non-negative numbers. Booleans, `NaN`, infinity,
and JSON numbers that overflow to infinity (such as `1e309`) are rejected.
RPM, TPM, and timeout must be greater than zero; retries and cost cap may be zero.
Fractional timeouts and costs remain supported. Invalid limits make both the
standalone preflight and the unified release check reject the configuration.

## Free Dry-Run

Use the helper without secret checking in public CI or local documentation checks:

```bash
python scripts/litellm_preflight.py --config configs/litellm-routes.example.json
```

This mode validates route integrity, fallback safety, capability declarations, route limits, and observability flags. It does not call providers and does not spend tokens.

## Structured CI Output

Use `--json` when a deployment gate needs to consume the result:

```bash
python scripts/litellm_preflight.py \
  --config configs/litellm-routes.example.json \
  --json
```

The command prints exactly one JSON object to standard output:

```json
{
  "errors": [],
  "live_probe_requested": false,
  "ok": true
}
```

The fields are stable:

- `ok` is `true` only when validation has no errors.
- `errors` contains individual validation or config-loading errors.
- `live_probe_requested` records whether `--live-probe` was requested; it does not imply that a provider call ran.

Invalid configurations still emit valid JSON and exit non-zero. JSON mode keeps standard error empty so CI can parse standard output as a single report. Without `--json`, the existing human-readable output remains the default.

## Secret Presence Check

Use the same helper with explicit secret presence checks in private deployment validation:

```bash
OPENAI_API_KEY=... ANTHROPIC_API_KEY=... \
  python scripts/litellm_preflight.py \
  --config configs/litellm-routes.example.json \
  --require-secrets
```

The script checks that the required environment variables exist, but it never prints secret values.

## Live Probes

Live provider checks must be opt-in. A production implementation can add a tiny provider probe, such as a one-token completion or a provider models endpoint request, but it should run only behind an explicit flag and never on every boot or in default CI.

The blueprint helper accepts `--live-probe` as a placeholder for this operational mode and intentionally makes no provider calls by default.
