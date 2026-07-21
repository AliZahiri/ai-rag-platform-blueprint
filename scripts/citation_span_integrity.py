from __future__ import annotations


def citation_span_violations(source_text: str, citations: list[dict[str, object]]) -> tuple[str, ...]:
    violations: list[str] = []
    for index, citation in enumerate(citations):
        prefix = f"citation_{index}"
        if not str(citation.get("source_id", "")).strip():
            violations.append(f"{prefix}_source_id_required")
        start = citation.get("start")
        end = citation.get("end")
        if (
            not isinstance(start, int)
            or isinstance(start, bool)
            or not isinstance(end, int)
            or isinstance(end, bool)
            or start < 0
            or end <= start
            or end > len(source_text)
        ):
            violations.append(f"{prefix}_span_out_of_bounds")
            continue
        quote = citation.get("quote")
        if not isinstance(quote, str) or source_text[start:end] != quote:
            violations.append(f"{prefix}_quote_mismatch")
    return tuple(violations)


def citation_spans_are_valid(source_text: str, citations: list[dict[str, object]]) -> bool:
    return bool(citations) and not citation_span_violations(source_text, citations)
