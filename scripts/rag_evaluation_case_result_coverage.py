from __future__ import annotations


def evaluation_case_result_coverage_violations(expected_case_ids: list[str], results: list[dict[str, object]]) -> tuple[str, ...]:
    violations: list[str] = []
    expected = [item.strip() for item in expected_case_ids if isinstance(item, str) and item.strip()]
    if not expected:
        violations.append("at_least_one_expected_case_is_required")
    if len(set(expected)) != len(expected):
        violations.append("expected_case_ids_must_be_unique")
    seen: set[str] = set()
    for index, result in enumerate(results if isinstance(results, list) else []):
        case_id = result.get("case_id") if isinstance(result, dict) else None
        if not isinstance(case_id, str) or not case_id.strip():
            violations.append(f"result_{index}:case_id_is_required")
            continue
        if case_id in seen:
            violations.append(f"result_{index}:case_id_must_be_unique")
        seen.add(case_id)
        if result.get("status") not in {"passed", "failed"}:
            violations.append(f"result_{index}:status_must_be_passed_or_failed")
    if set(expected) - seen:
        violations.append("expected_cases_are_missing_results")
    if seen - set(expected):
        violations.append("unexpected_case_results_are_present")
    return tuple(violations)


def evaluation_case_result_coverage_is_complete(expected_case_ids: list[str], results: list[dict[str, object]]) -> bool:
    return not evaluation_case_result_coverage_violations(expected_case_ids, results)
