# Add retrieval access-scope gate

<!-- daily-pr-task: retrieval-access-scope-gate -->

Retrieved context must remain within the caller's approved tenant and access scopes. This offline gate validates retrieval evidence before prompt assembly: every record has a unique chunk identity, a declared tenant, at least one scope, and an explicit granted access decision. It rejects records that cross the request tenant, omit the requested scope, or were not granted access. It does not call a vector store or provider.

## Portfolio Value

Extends RAG safety beyond quality and freshness by making authorization evidence a deterministic release condition before retrieved content reaches a model prompt.

## Validation

Run `python3 -m unittest discover -s tests` and confirm granted records within the requested tenant and scope pass while empty input, invalid request contracts, duplicate chunks, cross-tenant records, missing scopes, and denied access fail.
