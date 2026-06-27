from __future__ import annotations


def chunking_profile_warnings(profile: dict[str, object]) -> tuple[str, ...]:
    warnings: list[str] = []
    chunk_size = profile.get("chunk_size")
    overlap = profile.get("overlap")
    if not isinstance(chunk_size, int) or not 200 <= chunk_size <= 4000:
        warnings.append("chunk_size_must_be_between_200_and_4000")
    if not isinstance(overlap, int) or overlap < 0:
        warnings.append("overlap_must_be_non_negative")
    if isinstance(chunk_size, int) and isinstance(overlap, int) and overlap >= chunk_size:
        warnings.append("overlap_must_be_smaller_than_chunk_size")
    if not profile.get("parser_profile"):
        warnings.append("parser_profile_missing")
    if not profile.get("embedding_model"):
        warnings.append("embedding_model_missing")
    return tuple(warnings)


def chunking_profile_is_safe(profile: dict[str, object]) -> bool:
    return not chunking_profile_warnings(profile)
