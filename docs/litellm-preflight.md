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

## Free Dry-Run

Use the helper without secret checking in public CI or local documentation checks:

```bash
python scripts/litellm_preflight.py --config configs/litellm-routes.example.json
```

This mode validates route integrity, fallback safety, capability declarations, route limits, and observability flags. It does not call providers and does not spend tokens.

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
