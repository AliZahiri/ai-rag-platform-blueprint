import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.rag_index_evidence_binding import REQUIRED_FIELDS, evidence_binding_violations, main

NOW = datetime(2026, 9, 12, 6, tzinfo=timezone.utc)
EXPECTED = {field: ("sha256:" + "a" * 64 if "sha256" in field or "digest" in field else "approved-v1")
            for field in REQUIRED_FIELDS}


def evidence():
    return {**EXPECTED, "observed_at": "2026-09-12T05:59:00Z"}


class EvidenceBindingTests(unittest.TestCase):
    def test_matching_fresh_evidence_passes(self):
        self.assertEqual((), evidence_binding_violations(evidence(), expected=EXPECTED, now=NOW))

    def test_each_binding_field_must_match(self):
        for field in REQUIRED_FIELDS:
            for value in (None, "", "different", True, [], {}):
                with self.subTest(field=field, value=value):
                    violations = evidence_binding_violations({**evidence(), field: value}, expected=EXPECTED, now=NOW)
                    self.assertIn(field + ":binding_mismatch", violations)

    def test_invalid_stale_and_future_timestamps_fail(self):
        for observed in (None, True, [], "broken", "2026-09-12T06:00:00",
                         "2026-09-12T05:54:59Z", "2026-09-12T06:00:01Z"):
            with self.subTest(observed=observed):
                self.assertIn("observation_is_invalid_stale_or_future_dated",
                    evidence_binding_violations({**evidence(), "observed_at": observed}, expected=EXPECTED, now=NOW))

    def test_boundary_and_equivalent_timezone_pass(self):
        for observed in ("2026-09-12T05:55:00Z", "2026-09-12T06:00:00Z", "2026-09-12T09:29:00+03:30"):
            with self.subTest(observed=observed):
                self.assertEqual((), evidence_binding_violations({**evidence(), "observed_at": observed}, expected=EXPECTED, now=NOW))

    def test_invalid_policy_fails(self):
        for age in (0, -1, True, 1.5, float("nan"), float("inf")):
            with self.subTest(age=age), self.assertRaises(ValueError):
                evidence_binding_violations(evidence(), expected=EXPECTED, now=NOW, maximum_age_seconds=age)
        with self.assertRaises(ValueError):
            evidence_binding_violations(evidence(), expected=EXPECTED, now=NOW.replace(tzinfo=None))

    def test_approved_contract_and_digests_are_validated(self):
        for expected in (None, {}, {**EXPECTED, "unknown": "x"}, {**EXPECTED, REQUIRED_FIELDS[0]: ""}):
            with self.subTest(expected=expected), self.assertRaises(ValueError):
                evidence_binding_violations(evidence(), expected=expected, now=NOW)
        for field in REQUIRED_FIELDS:
            if "sha256" in field or "digest" in field:
                with self.assertRaises(ValueError):
                    evidence_binding_violations(evidence(), expected={**EXPECTED, field: "latest"}, now=NOW)

    def test_invalid_evidence_shape_is_rejected(self):
        self.assertEqual(("evidence_must_be_an_object",),
                         evidence_binding_violations([], expected=EXPECTED, now=NOW))

    def test_cli_exit_codes_distinguish_rejection_and_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            for manifest, code in (({"expected": EXPECTED, "evidence": evidence()}, 0),
                                   ({"expected": EXPECTED, "evidence": {}}, 1), ([], 2)):
                path.write_text(json.dumps(manifest))
                self.assertEqual(code, main([str(path), "--now", NOW.isoformat()]))
            path.write_text("{invalid")
            self.assertEqual(2, main([str(path), "--now", NOW.isoformat()]))
            self.assertEqual(2, main([str(path.parent / "missing.json"), "--now", NOW.isoformat()]))
