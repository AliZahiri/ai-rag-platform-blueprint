# Changelog

All notable changes to this project are documented in this file.

The project follows Semantic Versioning for public release snapshots. Policy
helpers and manifest schemas remain experimental unless their documentation
states otherwise.

## [0.2.0] - 2026-09-16

### Added

- A versioned, allowlisted offline RAG release-check manifest and aggregate
  runner with deterministic JSON output, bounded execution time, and distinct
  policy-rejection and execution-error exit codes.
- Release gates for LiteLLM route readiness, citation freshness, chat-history
  retention, vector backup coverage, and vector-index replica consistency.
- Offline controls for retrieval quality, citation traceability, evaluation
  integrity, privacy, response safety, token and cost budgets, provider
  reliability, index lifecycle, and restore evidence.
- Structured validation for corpus, embedding-model, index, evaluation, and
  provider evidence bindings.
- Tests for malformed UTF-8, unsafe Unicode arguments, invalid numeric values,
  timeout behavior, policy rejection, and partial gate failure.

### Changed

- GitHub Actions now uses the unified release manifest as the release-readiness
  check and declares read-only repository permissions explicitly.
- Daily portfolio automation now validates generated paths and isolates
  validation in a temporary worktree before proposing changes.
- GitHub Actions dependencies were upgraded to their Node 24-compatible major
  versions.

### Security

- Release checks execute only allowlisted Python entry points without a shell.
- Default validation remains offline and never requires provider credentials or
  paid API calls; provider liveness probing remains explicitly opt-in.
- Secret references, PII handling, data residency, fallback privacy, prompt
  injection evidence, and response redaction have dedicated policy controls.

### Compatibility

- The release-check manifest remains at schema version `1`.
- Existing documented CLI entry points and Docker Compose examples remain
  backward compatible with `v0.1.0`.
- No migration is required. Operators should review and version their release
  manifest before adopting the unified runner.

[0.2.0]: https://github.com/AliZahiri/ai-rag-platform-blueprint/compare/v0.1.0...v0.2.0
