from __future__ import annotations

REQUIRED_IDEMPOTENCY_FIELDS = ("document_id", "source_checksum", "parser_profile", "chunking_version")


def missing_idempotency_fields(metadata: dict[str, object]) -> tuple[str, ...]:
    return tuple(field for field in REQUIRED_IDEMPOTENCY_FIELDS if not metadata.get(field))


def ingestion_is_idempotent(metadata: dict[str, object]) -> bool:
    return not missing_idempotency_fields(metadata)
