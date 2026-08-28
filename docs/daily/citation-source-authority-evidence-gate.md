# Add citation source authority evidence gate

<!-- daily-pr-task: citation-source-authority-evidence-gate -->

High-impact RAG answers should not treat every cited source as equally authoritative. This offline gate validates unique source identities, explicit authority tiers, review evidence, and claim coverage, then requires each critical claim to be backed by at least one reviewed primary or official source. It validates supplied metadata only and does not infer source truth or contact external systems.

## Portfolio Value

Adds a reviewable authority layer to citation traceability so critical RAG claims cannot pass solely because low-authority sources are present.

## Validation

Run python3 -m unittest discover -s tests and confirm only reviewed primary or official sources cover critical claims while duplicate identities, invalid tiers, and malformed claim metadata fail.
