# Add vector database backup notes

<!-- daily-pr-task: vector-db-backup-notes -->

Vector database backup planning should cover both the vector collections and the source documents used to create them. A restore is incomplete if embeddings are restored but source files, parser settings, or collection metadata are missing.

Minimum backup targets:

- vector collections
- document source storage
- parser and chunking configuration
- embedding model metadata
- collection schema and index settings

## Portfolio Value

Highlights operational depth around RAG systems, especially restore readiness.

## Validation

Review the markdown file and confirm backup targets are clear and actionable.
