# Add retrieval evidence hash integrity gate

<!-- daily-pr-task: retrieval-evidence-hash-integrity-gate -->

Corpus lineage identifies a snapshot but does not prove that retrieved evidence still matches its immutable source manifest. This offline gate validates manifest SHA-256 values, unique source identities, and exact digest agreement for every retrieved record. It consumes metadata only and never reads source content or contacts a provider.

## Portfolio Value

Adds cryptographic evidence integrity to reproducible RAG evaluation so a matching snapshot label cannot hide altered or incorrectly indexed source content.

## Validation

Run `python3 -m unittest discover -s tests` and confirm matching immutable evidence passes while empty records, invalid manifests, duplicate or unknown sources, malformed digests, and digest mismatches fail.
