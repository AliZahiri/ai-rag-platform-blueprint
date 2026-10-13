# Retrieval Evaluation

`scripts/retrieval_evaluation.py` calculates Recall@k and MRR@k from a
reviewed export of ranked retrieval results. It is deterministic and does not
contact a provider, embedding service, or vector database, so it is suitable
for default CI and for comparing exported production evidence.

```bash
python3 scripts/retrieval_evaluation.py examples/retrieval-evaluation.example.json \
  --top-k 3 \
  --minimum-recall-at-k 0.80 \
  --minimum-mrr-at-k 0.80
```

The JSON evidence has one `cases` array. Every case must include a unique
`case_id`, non-empty unique `relevant_source_ids`, and unique ranked
`retrieved_source_ids`. Empty retrieved results are valid evidence and produce
zero quality scores; malformed or duplicate identifiers are rejected as input
errors instead of being silently repaired.

For each case, Recall@k is the fraction of relevant source IDs appearing in the
first `k` retrieved IDs. MRR@k is the reciprocal rank of the first relevant
source, or zero when none appears in the first `k`. The report includes
per-case metrics, failed case IDs, aggregate means, explicit thresholds, and a
machine-readable release decision.

Exit codes:

- `0`: both aggregate thresholds pass.
- `1`: valid evidence failed one or more quality thresholds.
- `2`: input or policy is invalid.

Evidence should be versioned or retained outside this repository according to
data-classification policy. Do not commit user prompts, private documents, or
customer identifiers merely to create an evaluation fixture.
