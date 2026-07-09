import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts/rag_backup_plan.py"
SPEC = importlib.util.spec_from_file_location("rag_backup_plan", SCRIPT_PATH)
rag_backup_plan = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rag_backup_plan)


class RagBackupPlanTests(unittest.TestCase):
    def test_complete_plan_has_no_missing_targets(self):
        self.assertTrue(rag_backup_plan.backup_plan_is_complete(rag_backup_plan.REQUIRED_BACKUP_TARGETS))

    def test_missing_targets_are_reported_in_required_order(self):
        missing = rag_backup_plan.missing_backup_targets({"vector_collections", "source_documents"})

        self.assertEqual(missing[0], "collection_metadata")
        self.assertIn("collection_schema", missing)

    def test_restore_verification_checks_are_required(self):
        missing = rag_backup_plan.missing_restore_checks({"collection_exists"})

        self.assertIn("sample_similarity_query", missing)
        self.assertIn("source_document_count_matches", missing)

    def test_backup_verification_requires_targets_and_restore_checks(self):
        self.assertTrue(
            rag_backup_plan.backup_verification_is_complete(
                rag_backup_plan.REQUIRED_BACKUP_TARGETS,
                rag_backup_plan.REQUIRED_RESTORE_CHECKS,
            )
        )
        self.assertFalse(
            rag_backup_plan.backup_verification_is_complete(
                {"vector_collections", "source_documents"},
                rag_backup_plan.REQUIRED_RESTORE_CHECKS,
            )
        )


if __name__ == "__main__":
    unittest.main()
