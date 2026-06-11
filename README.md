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

## Production Notes

- Pin all container images before production use.
- Keep model files, secrets, and customer data outside Git.
- Separate GPU inference nodes from application and database nodes when capacity grows.
- Measure both time-to-first-token and full response time.
- Treat `200 concurrent users` and `200 concurrent generations` as different sizing inputs.
- Add backups for PostgreSQL, vector storage, uploaded files, and model configuration.
- Add centralized logs before production support begins.

## Security Notes

- Do not commit API keys, model tokens, database passwords, or private documents.
- Put gateway auth, rate limiting, and request size limits in front of the RAG layer.
- Restrict admin UIs and model-serving APIs to trusted networks.
- Document retention rules for chat history and uploaded knowledge-base files.

## Next Iterations

- Add Kong or Nginx gateway examples
- Add LiteLLM config examples
- Add vLLM GPU node runbook
- Add backup and restore runbooks
- Add benchmark plan for model and GPU sizing
