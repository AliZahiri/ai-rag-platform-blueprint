# AI RAG Platform Blueprint

Reference architecture for running an internal AI, LLM, and RAG platform on production-oriented infrastructure.

This repository focuses on the platform layer around AI systems: gateway, routing, model serving, vector storage, databases, observability, deployment boundaries, and operational notes. It is not a model training project.

## Architecture

```text
Client / Internal App
        |
        v
API Gateway / Reverse Proxy
        |
        v
RAG Orchestrator
        |
        v
LLM Router
        |
        v
GPU Inference Backend

Supporting services:
PostgreSQL, Redis, Vector DB, object/artifact storage, monitoring, logs, backups
```

See [docs/architecture.md](docs/architecture.md) and [diagrams/request-flow.mmd](diagrams/request-flow.mmd).
See [docs/litellm-preflight.md](docs/litellm-preflight.md) for the LiteLLM fail-fast validation checklist.

## Components

- **Gateway:** public/internal entrypoint, timeouts, request limits, access logs, and routing policy
- **RAG Orchestrator:** Dify or similar workflow layer for chat, knowledge base, prompt workflow, and retrieval
- **LLM Router:** LiteLLM-style routing layer for model abstraction and future multi-backend support
- **Inference:** vLLM-style OpenAI-compatible model serving on GPU nodes
- **State:** PostgreSQL for metadata and conversation state, Redis for queues/cache
- **Vector DB:** Qdrant, Milvus, Weaviate, pgvector, or another validated vector store
- **Observability:** Prometheus, Grafana, logs, health checks, latency and error tracking

## Repository Structure

```text
.
├── compose/                 # Docker Compose blueprint
├── diagrams/                # Mermaid architecture diagrams
├── docs/                    # Architecture and operations notes
├── env/                     # Environment examples
├── monitoring/              # Prometheus starter config
└── scripts/                 # Operational helper scripts
```

## Quick Start

This is a blueprint. Review and pin images before using it outside a lab.

```bash
cp env/.env.example .env
docker compose -f compose/docker-compose.yml --env-file .env config
docker compose -f compose/docker-compose.yml --env-file .env up -d
./scripts/check-stack.sh
```

Citation metadata can be checked with a deterministic release gate before an answer is exposed:

```bash
python3 scripts/citation_freshness_release.py citation-sources.json --today 2026-07-28 --max-age-days 90
```

The command prints a JSON report and exits non-zero when source identity, status, or review freshness fails.

Chat-history retention policies can use the same offline release-gate approach:

```bash
python3 scripts/chat_retention_policy_gate.py retention-policy.json
```

See [the retention policy gate](docs/chat-retention-policy-gate.md) for its JSON
contract, deterministic output, and CI use.

## Offline Release Gates

The repository includes executable, provider-free gates for CI and release
workflows. They validate configuration or supplied evidence without contacting a
model provider by default.

| Gate | Entry point | Operational decision |
| --- | --- | --- |
| LiteLLM route preflight | `scripts/litellm_preflight.py` | Route, fallback, capability, secret-reference, and observability readiness |
| Citation freshness | `scripts/citation_freshness_release.py` | Whether cited sources are identifiable and recently reviewed |
| Chat retention | `scripts/chat_retention_policy_gate.py` | Whether retention policy fields and review controls are complete |
| Vector backup coverage | `scripts/rag_backup_plan.py` | Whether backup targets and restore checks cover the RAG data plane |
| Index replica consistency | `scripts/index_replica_consistency.py` | Whether fresh replicas match the approved generation, count, and digest |

Each command documents its arguments through `--help`; the related operational
contracts live under `docs/`. Provider liveness remains explicitly opt-in.

## Production Notes

- Pin all container images before production use.
- Keep model files, secrets, and customer data outside Git.
- Separate GPU inference nodes from application and database nodes when capacity grows.
- Measure both time-to-first-token and full response time.
- Treat `200 concurrent users` and `200 concurrent generations` as different sizing inputs.
- Add backups for PostgreSQL, vector storage, uploaded files, and model configuration.
- Add centralized logs before production support begins.
- Validate LiteLLM route integrity, fallback chains, secret presence, capabilities, and observability before traffic reaches model routes.

## Security Notes

- Do not commit API keys, model tokens, database passwords, or private documents.
- Put gateway auth, rate limiting, and request size limits in front of the RAG layer.
- Restrict admin UIs and model-serving APIs to trusted networks.
- Document retention rules for chat history and uploaded knowledge-base files.

## Next Iterations

- Consolidate the standalone policy modules behind versioned JSON schemas and a
  unified release-check command.
- Add opt-in evidence collectors for LiteLLM, the vector store, and Prometheus
  while keeping default CI provider-free.
- Pin default container references by digest and document the upgrade workflow.
- Turn the current GPU and vector-restore guidance into runnable drill examples.
