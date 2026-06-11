# Architecture Notes

## Goal

Provide a practical platform architecture for teams that need an internal AI/RAG service without building every orchestration layer from scratch.

The design keeps the platform modular so each layer can be replaced or scaled independently.

## Request Flow

1. A client or internal system sends a request to the gateway.
2. The gateway applies routing, timeouts, request limits, and logging.
3. The RAG orchestrator receives the user prompt and builds the retrieval workflow.
4. The orchestrator reads metadata and conversation state from PostgreSQL and Redis.
5. The orchestrator queries the vector database for relevant document context.
6. The LLM router chooses the configured model backend.
7. The inference backend generates the response.
8. Logs and metrics are collected for troubleshooting and capacity planning.

## Deployment Boundaries

- The gateway owns ingress policy.
- The RAG orchestrator owns workflow, prompt, knowledge base, and conversation behavior.
- The LLM router owns model endpoint abstraction.
- The inference backend owns GPU execution and model runtime.
- PostgreSQL, Redis, and vector storage must have independent backup and restore plans.

## Scaling Approach

- Add more gateway instances behind an upstream load balancer.
- Add more RAG workers when workflow throughput becomes the bottleneck.
- Add more LLM router instances for endpoint redundancy.
- Add GPU inference nodes based on benchmark results.
- Scale the vector database based on document count, query volume, and latency.

## Sizing Inputs

Important inputs for capacity planning:

- Selected model and quantization
- GPU model and available VRAM
- Context length
- Average input tokens
- Average output tokens
- Active concurrent generations
- Streaming versus non-streaming responses
- Retrieval count and reranking cost
- OCR and document processing volume
