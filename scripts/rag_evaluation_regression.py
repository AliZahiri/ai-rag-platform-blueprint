from __future__ import annotations

import argparse
import json
from math import isfinite
from pathlib import Path
import sys


_METRICS = ("groundedness", "citation_precision", "answer_relevance")


def _valid_score(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(float(value)) and 0 <= float(value) <= 1


def evaluation_regression_violations(*, baseline: dict[str, object], candidate: dict[str, object], maximum_regression: float) -> tuple[str, ...]:
    if not _valid_score(maximum_regression):
        raise ValueError("maximum regression must be between zero and one")
    violations: list[str] = []
    for metric in _METRICS:
        baseline_score = baseline.get(metric)
        candidate_score = candidate.get(metric)
        if not _valid_score(baseline_score):
            violations.append(f"baseline:{metric}:score_must_be_between_zero_and_one")
            continue
        if not _valid_score(candidate_score):
            violations.append(f"candidate:{metric}:score_must_be_between_zero_and_one")
            continue
        if float(baseline_score) - float(candidate_score) > maximum_regression:
            violations.append(f"{metric}:regression_exceeds_budget")
    return tuple(violations)


def evaluation_regression_is_acceptable(**inputs: object) -> bool:
    return not evaluation_regression_violations(**inputs)


def load_evaluation_scores(
    path: Path,
) -> tuple[dict[str, object], dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("evaluation regression input must be a JSON object")
    baseline = payload.get("baseline")
    candidate = payload.get("candidate")
    if not isinstance(baseline, dict):
        raise ValueError("baseline must be a JSON object")
    if not isinstance(candidate, dict):
        raise ValueError("candidate must be a JSON object")
    return baseline, candidate


def evaluation_regression_report(
    *,
    baseline: dict[str, object],
    candidate: dict[str, object],
    maximum_regression: float,
) -> dict[str, object]:
    violations = evaluation_regression_violations(
        baseline=baseline,
        candidate=candidate,
        maximum_regression=maximum_regression,
    )
    return {
        "maximum_regression": maximum_regression,
        "metrics": list(_METRICS),
        "status": "pass" if not violations else "fail",
        "violations": list(violations),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reject RAG releases whose offline evaluation metrics regress."
    )
    parser.add_argument("evidence", type=Path, help="JSON baseline and candidate scores")
    parser.add_argument("--maximum-regression", required=True, type=float)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        baseline, candidate = load_evaluation_scores(args.evidence)
        report = evaluation_regression_report(
            baseline=baseline,
            candidate=candidate,
            maximum_regression=args.maximum_regression,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        print(json.dumps({"error": str(error), "status": "error"}), file=sys.stderr)
        return 2

    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
