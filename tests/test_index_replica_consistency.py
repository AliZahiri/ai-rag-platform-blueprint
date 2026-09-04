import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from io import StringIO
import json
from pathlib import Path
import tempfile

from scripts.index_replica_consistency import (
    index_replica_consistency_violations,
    index_replicas_are_consistent,
    main,
)


NOW = datetime(2026, 9, 4, 6, 0, tzinfo=timezone.utc)
DIGEST = "sha256:" + "a" * 64
POLICY = {"expected_generation": "generation-42", "expected_document_count": 1200, "expected_sha256": DIGEST, "now": NOW}


class IndexReplicaConsistencyEvidenceTests(unittest.TestCase):
    def matching_replicas(self):
        return [
            {
                "replica_id": name,
                "healthy": True,
                "index_generation": "generation-42",
                "document_count": 1200,
                "index_sha256": DIGEST,
                "observed_at": "2026-09-04T05:55:00Z",
            }
            for name in ("az-a", "az-b")
        ]

    def test_two_fresh_matching_replicas_pass(self):
        self.assertTrue(index_replicas_are_consistent(self.matching_replicas(), **POLICY))

    def test_stale_and_divergent_replica_fails(self):
        replicas = [{"replica_id": "az-a", "healthy": True, "index_generation": "generation-42", "document_count": 1200, "index_sha256": DIGEST, "observed_at": "2026-09-04T05:55:00Z"}, {"replica_id": "az-b", "healthy": False, "index_generation": "generation-41", "document_count": 1190, "index_sha256": "sha256:" + "b" * 64, "observed_at": "2026-09-04T04:00:00Z"}]
        violations = index_replica_consistency_violations(replicas, **POLICY)
        self.assertIn("replica_1:must_be_healthy", violations)
        self.assertIn("replica_1:generation_mismatch", violations)
        self.assertIn("replica_1:digest_mismatch", violations)
        self.assertIn("replica_1:observation_is_invalid_stale_or_future_dated", violations)

    def test_replica_quorum_and_policy_are_validated(self):
        self.assertEqual(("minimum_index_replica_count_not_met",), index_replica_consistency_violations([], **POLICY))
        with self.assertRaises(ValueError):
            index_replica_consistency_violations([], **{**POLICY, "minimum_replicas": 1})

    def test_cli_emits_machine_readable_pass_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            evidence = Path(temp_dir) / "evidence.json"
            evidence.write_text(
                json.dumps({"replicas": self.matching_replicas()}), encoding="utf-8"
            )
            output = StringIO()
            with redirect_stdout(output):
                exit_code = main(
                    [
                        str(evidence),
                        "--expected-generation",
                        "generation-42",
                        "--expected-document-count",
                        "1200",
                        "--expected-sha256",
                        DIGEST,
                        "--now",
                        "2026-09-04T06:00:00Z",
                    ]
                )

        report = json.loads(output.getvalue())
        self.assertEqual(0, exit_code)
        self.assertEqual("pass", report["status"])
        self.assertEqual(2, report["replica_count"])
        self.assertEqual([], report["violations"])

    def test_cli_returns_one_for_policy_violations(self):
        replicas = self.matching_replicas()
        replicas[1]["healthy"] = False
        with tempfile.TemporaryDirectory() as temp_dir:
            evidence = Path(temp_dir) / "evidence.json"
            evidence.write_text(json.dumps({"replicas": replicas}), encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                exit_code = main(
                    [
                        str(evidence),
                        "--expected-generation",
                        "generation-42",
                        "--expected-document-count",
                        "1200",
                        "--expected-sha256",
                        DIGEST,
                        "--now",
                        "2026-09-04T06:00:00Z",
                    ]
                )

        report = json.loads(output.getvalue())
        self.assertEqual(1, exit_code)
        self.assertEqual("fail", report["status"])
        self.assertIn("replica_1:must_be_healthy", report["violations"])

    def test_cli_returns_two_for_malformed_input(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            evidence = Path(temp_dir) / "evidence.json"
            evidence.write_text("not-json", encoding="utf-8")
            error = StringIO()
            with redirect_stderr(error):
                exit_code = main(
                    [
                        str(evidence),
                        "--expected-generation",
                        "generation-42",
                        "--expected-document-count",
                        "1200",
                        "--expected-sha256",
                        DIGEST,
                    ]
                )

        report = json.loads(error.getvalue())
        self.assertEqual(2, exit_code)
        self.assertEqual("error", report["status"])
