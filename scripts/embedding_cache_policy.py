from __future__ import annotations

REQUIRED_CACHE_KEY_FIELDS = ("document_id", "content_checksum", "parser_profile", "embedding_model")


def missing_cache_key_fields(metadata: dict[str, object]) -> tuple[str, ...]:
    return tuple(field for field in REQUIRED_CACHE_KEY_FIELDS if not metadata.get(field))


def embedding_cache_key_is_stable(metadata: dict[str, object]) -> bool:
    return not missing_cache_key_fields(metadata)


def build_embedding_cache_key(metadata: dict[str, object]) -> str:
    missing = missing_cache_key_fields(metadata)
    if missing:
        raise ValueError(f"missing cache key fields: {', '.join(missing)}")
    return ":".join(str(metadata[field]).strip().lower() for field in REQUIRED_CACHE_KEY_FIELDS)
