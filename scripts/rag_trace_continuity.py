from __future__ import annotations


_REQUIRED_STAGES = ("retrieval", "generation", "citation")


def trace_continuity_violations(evidence: dict[str, object]) -> tuple[str, ...]:
    violations: list[str] = []
    for field in ("request_id", "trace_id"):
        if not isinstance(evidence.get(field), str) or not evidence[field].strip():
            violations.append(f"{field}_is_required")
    trace_id = evidence.get("trace_id")
    spans = evidence.get("spans")
    if not isinstance(spans, list) or not spans:
        return tuple([*violations, "at_least_one_trace_span_is_required"])
    seen_span_ids: set[str] = set()
    stages: dict[str, dict[str, object]] = {}
    for index, span in enumerate(spans):
        if not isinstance(span, dict):
            violations.append(f"span_{index}:must_be_an_object")
            continue
        span_id = span.get("span_id")
        if not isinstance(span_id, str) or not span_id.strip():
            violations.append(f"span_{index}:span_id_is_required")
        elif span_id in seen_span_ids:
            violations.append(f"span_{index}:span_id_must_be_unique")
        else:
            seen_span_ids.add(span_id)
        stage = span.get("stage")
        if stage not in _REQUIRED_STAGES:
            violations.append(f"span_{index}:stage_is_invalid")
        elif stage in stages:
            violations.append(f"span_{index}:stage_must_be_unique")
        else:
            stages[stage] = span
        if not isinstance(trace_id, str) or span.get("trace_id") != trace_id:
            violations.append(f"span_{index}:trace_id_must_match")
        if span.get("status") != "ok":
            violations.append(f"span_{index}:status_must_be_ok")
    for stage in _REQUIRED_STAGES:
        if stage not in stages:
            violations.append(f"{stage}_span_is_required")
    if all(stage in stages for stage in _REQUIRED_STAGES):
        if stages["generation"].get("parent_span_id") != stages["retrieval"].get("span_id"):
            violations.append("generation_must_descend_from_retrieval")
        if stages["citation"].get("parent_span_id") != stages["generation"].get("span_id"):
            violations.append("citation_must_descend_from_generation")
    return tuple(violations)


def rag_trace_is_continuous(evidence: dict[str, object]) -> bool:
    return not trace_continuity_violations(evidence)
