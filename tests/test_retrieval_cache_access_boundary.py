import unittest

from scripts.retrieval_cache_access_boundary import (
    retrieval_cache_access_is_safe,
    retrieval_cache_access_violations,
)


class RetrievalCacheAccessBoundaryGateTests(unittest.TestCase):
    def test_cache_entry_bound_to_request_tenant_and_scope_passes(self):
        entry = {
            "cache_key": "acme:handbook:42",
            "tenant": "acme",
            "scopes": ["knowledge.read"],
            "access_decision": "granted",
        }

        self.assertTrue(
            retrieval_cache_access_is_safe(
                entry, tenant="acme", required_scope="knowledge.read"
            )
        )

    def test_cross_tenant_or_unapproved_cache_entry_fails(self):
        violations = retrieval_cache_access_violations(
            {
                "cache_key": "",
                "tenant": "other",
                "scopes": ["profile.read"],
                "access_decision": "denied",
            },
            tenant="acme",
            required_scope="knowledge.read",
        )

        self.assertEqual(
            violations,
            (
                "cache_key_is_required",
                "cache_tenant_must_match_request",
                "required_scope_is_missing_from_cache_entry",
                "cache_access_must_be_granted",
            ),
        )


if __name__ == "__main__":
    unittest.main()
