# Add RAG answer abstention evidence gate

<!-- daily-pr-task: rag-answer-abstention-evidence-gate -->

A RAG service should decline to answer when retrieval confidence, groundedness, or citation evidence is insufficient. This provider-free gate validates a structured answer decision and prevents an `answer` outcome from passing when its confidence is below policy, groundedness is weak, or no citations are attached. Explicit abstentions remain valid only when they carry a reviewable reason.

## Portfolio Value

Turns unsupported-answer handling into an executable release contract and demonstrates explicit fail-closed behavior without sending prompts, documents, or paid model requests through CI.

## Validation

Run python3 -m unittest discover -s tests and confirm grounded cited answers and explained abstentions pass while low-confidence, weakly grounded, uncited, malformed, and unexplained decisions fail.
