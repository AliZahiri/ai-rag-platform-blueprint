from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


def retrieval_prompt_injection_violations(chunks: list[dict[str, object]]) -> tuple[str, ...]:
    if not chunks:
        return ("at_least_one_retrieval_chunk_is_required",)
    violations: list[str] = []
    seen: set[str] = set()
    for position, chunk in enumerate(chunks):
        if not isinstance(chunk, dict):
            violations.append(f"chunk_{position}:must_be_an_object")
            continue
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


def load_retrieval_chunks(path: Path) -> list[dict[str, object]]:
    """Load scanner evidence from a deliberately narrow, versionable shape."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("retrieval prompt-injection input must be a JSON object")
    chunks = payload.get("chunks")
    if not isinstance(chunks, list):
        raise ValueError("chunks must be a JSON array")
    return chunks


def retrieval_prompt_injection_report(chunks: list[dict[str, object]]) -> dict[str, object]:
    violations = retrieval_prompt_injection_violations(chunks)
    return {
        "chunk_count": len(chunks),
        "status": "pass" if not violations else "fail",
        "violations": list(violations),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate retrieval prompt-injection containment evidence."
    )
    parser.add_argument("evidence", type=Path, help="JSON object containing a chunks array")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = retrieval_prompt_injection_report(load_retrieval_chunks(args.evidence))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        print(json.dumps({"error": str(error), "status": "error"}, sort_keys=True), file=sys.stderr)
        return 2

    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
