# LiteLLM Routing Responsibilities

LiteLLM should act as the model endpoint abstraction layer. It keeps the RAG
orchestrator independent from a specific inference backend and makes future
model changes less disruptive.

Operational responsibilities:

- expose one stable endpoint to the RAG layer
- route requests to one or more model backends
- isolate model naming from application code
- support gradual backend changes
- provide a clear place for retries, budgets, and model policy

For portfolio review, this documents the boundary between application code,
model routing, and inference infrastructure. That boundary matters when a team
wants to compare hosted APIs, local vLLM, or fallback models without rewriting
the RAG workflow.
