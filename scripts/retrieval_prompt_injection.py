from __future__ import annotations


def retrieval_prompt_injection_violations(chunks: list[dict[str, object]]) -> tuple[str, ...]:
    if not chunks:
        return ("at_least_one_retrieval_chunk_is_required",)
    violations: list[str] = []
    seen: set[str] = set()
    for position, chunk in enumerate(chunks):
        chunk_id = str(chunk.get("chunk_id", "")).strip()
        if not chunk_id:
            violations.append(f"chunk_{position}:chunk_id_is_required")
        elif chunk_id in seen:
            violations.append(f"chunk_{position}:chunk_id_must_be_unique")
        seen.add(chunk_id)
        trust = chunk.get("trust_level")
        if trust not in {"trusted", "untrusted"}:
            violations.append(f"chunk_{position}:trust_level_is_invalid")
        signals = chunk.get("instruction_signal_count")
        if not isinstance(signals, int) or isinstance(signals, bool) or signals < 0:
            violations.append(f"chunk_{position}:instruction_signal_count_must_be_non_negative")
            continue
        if trust == "untrusted" and signals > 0:
            if chunk.get("quarantined") is not True:
                violations.append(f"chunk_{position}:untrusted_instruction_signals_require_quarantine")
            if chunk.get("eligible_for_context") is not False:
                violations.append(f"chunk_{position}:quarantined_chunk_must_be_excluded_from_context")
        if chunk.get("quarantined") is True and chunk.get("eligible_for_context") is not False:
            violations.append(f"chunk_{position}:quarantined_chunk_cannot_be_context_eligible")
    return tuple(violations)


def retrieval_context_is_injection_safe(chunks: list[dict[str, object]]) -> bool:
    return not retrieval_prompt_injection_violations(chunks)
