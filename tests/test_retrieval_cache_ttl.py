import unittest

from scripts.retrieval_cache_ttl import retrieval_cache_entry_is_safe, retrieval_cache_violations


class RetrievalCacheTtlContractTests(unittest.TestCase):
    def test_bounded_non_sensitive_entry_passes(self):
        entry = {"cache_key": "handbook:42", "citation_scope": "handbook", "ttl_seconds": 300, "cached_at": "2026-08-20T12:00:00Z", "contains_sensitive_data": False}
        self.assertTrue(retrieval_cache_entry_is_safe(entry))

    def test_unbounded_or_sensitive_entry_fails(self):
        violations = retrieval_cache_violations({"cache_key": "", "citation_scope": "", "ttl_seconds": 7200, "cached_at": "2026-08-20T12:00:00", "contains_sensitive_data": True}, max_ttl_seconds=600)
        self.assertEqual(violations, ("cache_key_is_required", "citation_scope_is_required", "ttl_seconds_must_be_within_policy", "cached_at_must_be_timezone_aware", "sensitive_entries_must_not_be_cached"))
