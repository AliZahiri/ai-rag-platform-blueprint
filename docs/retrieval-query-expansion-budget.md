# Retrieval query expansion budget

Query expansion can improve recall, but an unbounded expansion stage also multiplies vector queries, reranking work, latency, and noisy evidence. The offline validator in `scripts/retrieval_query_expansion_budget.py` makes that fan-out explicit before a request reaches a vector store or paid provider.

The gate requires a non-empty original query, preserves that query in the expanded set, rejects blank or case-insensitive duplicate entries, and enforces configurable count and character budgets. It validates supplied strings only; it does not generate queries or call a model.

Run the focused tests with:

```bash
python3 -m unittest tests.test_retrieval_query_expansion_budget
```

Tune the budgets from measured retrieval latency and quality data. A passing result proves only that expansion is bounded and reviewable, not that the generated queries improve retrieval quality.
