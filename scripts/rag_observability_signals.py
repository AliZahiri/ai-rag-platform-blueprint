from __future__ import annotations

REQUIRED_RAG_SIGNALS = (
    "retrieval_latency_seconds",
    "vector_db_query_latency_seconds",
    "retrieved_document_count",
    "empty_retrieval_total",
    "model_latency_seconds",
    "model_token_throughput",
    "request_errors_total",
    "gpu_memory_utilization",
)


def missing_rag_signals(enabled_signals: list[str] | tuple[str, ...] | set[str]) -> tuple[str, ...]:
    enabled = set(enabled_signals)
    return tuple(signal for signal in REQUIRED_RAG_SIGNALS if signal not in enabled)


def rag_observability_is_complete(enabled_signals: list[str] | tuple[str, ...] | set[str]) -> bool:
    return not missing_rag_signals(enabled_signals)
