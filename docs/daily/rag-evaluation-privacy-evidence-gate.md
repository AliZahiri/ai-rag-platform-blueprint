# Add RAG evaluation privacy evidence gate

<!-- daily-pr-task: rag-evaluation-privacy-evidence-gate -->

Evaluation data can expose the same customer and sensitive information as production traffic. This offline gate validates evidence that an evaluation snapshot is identified, approved, scanned for sensitive data, redacted where required, and reviewed within a bounded age. It validates supplied metadata only and never contacts an LLM provider or reads the dataset itself.

## Portfolio Value

Makes evaluation governance credible by requiring privacy-review evidence without placing customer data or provider calls in CI.

## Validation

Run `python3 -m unittest discover -s tests`; confirm a recent approved snapshot passes and missing privacy controls, stale reviews, invalid policies, or future review dates fail deterministically.
