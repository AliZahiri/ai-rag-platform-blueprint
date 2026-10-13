from __future__ import annotations

import argparse
import json
from math import isfinite
from pathlib import Path
import sys


def _probability(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and isfinite(float(value))
        and 0 <= float(value) <= 1
    )


def _positive_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _source_ids(value: object, *, field: str, allow_empty: bool) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        raise ValueError(f"{field} must be a {'possibly empty ' if allow_empty else 'non-empty '}array")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"{field} must contain non-empty strings")
    if len(set(value)) != len(value):
        raise ValueError(f"{field} must not contain duplicate source IDs")
    return value


def validate_cases(cases: object) -> list[dict[str, object]]:
    """Validate ranked retrieval evidence without contacting a provider or vector store."""
    if not isinstance(cases, list) or not cases:
        raise ValueError("cases must be a non-empty array")

    normalized: list[dict[str, object]] = []
    seen_case_ids: set[str] = set()
    for index, case in enumerate(cases):
        prefix = f"cases[{index}]"
        if not isinstance(case, dict):
            raise ValueError(f"{prefix} must be an object")
        if set(case) != {"case_id", "relevant_source_ids", "retrieved_source_ids"}:
            raise ValueError(
                f"{prefix} must contain only case_id, relevant_source_ids, and retrieved_source_ids"
            )
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError(f"{prefix}.case_id must be a non-empty string")
        if case_id in seen_case_ids:
            raise ValueError("case_id values must be unique")
        seen_case_ids.add(case_id)
        normalized.append(
            {
                "case_id": case_id,
                "relevant_source_ids": _source_ids(
                    case.get("relevant_source_ids"),
                    field=f"{prefix}.relevant_source_ids",
                    allow_empty=False,
                ),
                "retrieved_source_ids": _source_ids(
                    case.get("retrieved_source_ids"),
                    field=f"{prefix}.retrieved_source_ids",
                    allow_empty=True,
                ),
            }
        )
    return normalized


def retrieval_evaluation_report(
    cases: object,
    *,
    top_k: int,
    minimum_recall_at_k: float,
    minimum_mrr_at_k: float,
) -> dict[str, object]:
    """Calculate deterministic retrieval quality metrics for ranked case evidence."""
    if not _positive_integer(top_k):
        raise ValueError("top_k must be a positive integer")
    if not _probability(minimum_recall_at_k):
        raise ValueError("minimum_recall_at_k must be a probability")
    if not _probability(minimum_mrr_at_k):
        raise ValueError("minimum_mrr_at_k must be a probability")

    normalized_cases = validate_cases(cases)
    case_results: list[dict[str, object]] = []
    for case in normalized_cases:
        relevant = set(case["relevant_source_ids"])
        retrieved = list(case["retrieved_source_ids"])[:top_k]
        relevant_positions = [
            position
            for position, source_id in enumerate(retrieved, start=1)
            if source_id in relevant
        ]
        relevant_retrieved = len(relevant_positions)
        case_results.append(
            {
                "case_id": case["case_id"],
                "recall_at_k": relevant_retrieved / len(relevant),
                "reciprocal_rank_at_k": 1 / relevant_positions[0]
                if relevant_positions
                else 0.0,
                "relevant_retrieved": relevant_retrieved,
            }
        )

    case_count = len(case_results)
    mean_recall = sum(float(result["recall_at_k"]) for result in case_results) / case_count
    mean_mrr = sum(float(result["reciprocal_rank_at_k"]) for result in case_results) / case_count
    violations: list[str] = []
    if mean_recall < minimum_recall_at_k:
        violations.append("mean_recall_at_k_below_minimum")
    if mean_mrr < minimum_mrr_at_k:
        violations.append("mean_mrr_at_k_below_minimum")

    return {
        "case_count": case_count,
        "case_results": case_results,
        "failed_case_ids": [
            result["case_id"]
            for result in case_results
            if result["relevant_retrieved"] == 0
        ],
        "metrics": {
            "mean_recall_at_k": mean_recall,
            "mean_mrr_at_k": mean_mrr,
        },
        "status": "pass" if not violations else "fail",
        "thresholds": {
            "minimum_recall_at_k": minimum_recall_at_k,
            "minimum_mrr_at_k": minimum_mrr_at_k,
            "top_k": top_k,
        },
        "violations": violations,
    }


def load_cases(path: Path) -> object:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or set(payload) != {"cases"}:
        raise ValueError("evaluation evidence must be an object containing only cases")
    return payload["cases"]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calculate provider-free Recall@k and MRR@k from ranked retrieval evidence."
    )
    parser.add_argument("evidence", type=Path, help="JSON retrieval evaluation evidence")
    parser.add_argument("--top-k", required=True, type=int)
    parser.add_argument("--minimum-recall-at-k", required=True, type=float)
    parser.add_argument("--minimum-mrr-at-k", required=True, type=float)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = retrieval_evaluation_report(
            load_cases(args.evidence),
            top_k=args.top_k,
            minimum_recall_at_k=args.minimum_recall_at_k,
            minimum_mrr_at_k=args.minimum_mrr_at_k,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        print(json.dumps({"error": str(error), "status": "error"}, sort_keys=True), file=sys.stderr)
        return 2

    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
