import unittest

from scripts.retrieval_access_scope import retrieval_access_scope_is_safe, retrieval_access_scope_violations


class RetrievalAccessScopeGateTests(unittest.TestCase):
    def test_granted_records_for_the_request_scope_pass(self):
        records = [{"chunk_id": "handbook-1", "tenant": "acme", "scopes": ["knowledge.read"], "access_decision": "granted"}]

        self.assertTrue(retrieval_access_scope_is_safe(records, tenant="acme", required_scope="knowledge.read"))

    def test_cross_tenant_scope_and_decision_failures_are_reported(self):
        records = [{"chunk_id": "handbook-1", "tenant": "other", "scopes": ["profile.read"], "access_decision": "denied"}, {"chunk_id": "handbook-1", "tenant": "acme", "scopes": [], "access_decision": "granted"}]

        violations = retrieval_access_scope_violations(records, tenant="acme", required_scope="knowledge.read")

        self.assertIn("record_0:tenant_must_match_request", violations)
        self.assertIn("record_0:required_scope_is_missing", violations)
        self.assertIn("record_0:access_must_be_granted", violations)
        self.assertIn("record_1:chunk_id_must_be_unique", violations)
        self.assertIn("record_1:scopes_must_be_a_non_empty_string_list", violations)

    def test_empty_records_and_invalid_request_contract_fail(self):
        self.assertEqual(("at_least_one_retrieval_record_is_required",), retrieval_access_scope_violations([], tenant="acme", required_scope="knowledge.read"))
        with self.assertRaises(ValueError):
            retrieval_access_scope_violations([], tenant="", required_scope="knowledge.read")


if __name__ == "__main__":
    unittest.main()
