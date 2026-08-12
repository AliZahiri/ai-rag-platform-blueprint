# Add retrieval source license gate

<!-- daily-pr-task: retrieval-source-license-gate -->

Retrieval corpora need license and reuse evidence as well as freshness and citations. This offline gate validates source metadata: unique source IDs, an allowed SPDX-style license, an explicit ingestion permission, and a declared owner. It rejects unlicensed or disallowed sources before they are approved for an index.

## Portfolio Value

Adds practical governance to RAG ingestion so the portfolio demonstrates that retrievability does not override content ownership and reuse constraints.

## Validation

Run `python3 -m unittest discover -s tests` and confirm permitted owned sources pass while empty, duplicate, unlicensed, unpermitted, and unowned source records fail.
