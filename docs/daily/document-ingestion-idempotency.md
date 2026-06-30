# Add document ingestion idempotency policy

<!-- daily-pr-task: document-ingestion-idempotency -->

Document ingestion should be idempotent so retries do not duplicate chunks or embeddings. The idempotency key should include document identity and ingestion settings.

Key fields:

- document id
- source checksum
- parser profile
- chunking version

## Portfolio Value

Shows ingestion jobs can be retried without duplicating vector records.

## Validation

Run the unit test and confirm idempotency keys require document and parser metadata.
