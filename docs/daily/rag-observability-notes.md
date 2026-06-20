# Document RAG observability signals

<!-- daily-pr-task: rag-observability-notes -->

RAG observability should track more than HTTP uptime. Retrieval quality and model behavior affect user experience and incident diagnosis.

Useful signals:

- retrieval latency
- vector DB query latency
- retrieved document count
- empty retrieval rate
- model latency and token throughput
- request error rate by gateway, RAG layer, router, and backend
- GPU memory and utilization

## Portfolio Value

Shows that observability is treated as part of AI platform architecture, not an afterthought.

## Validation

Review the markdown file and confirm the signals map to platform components.
