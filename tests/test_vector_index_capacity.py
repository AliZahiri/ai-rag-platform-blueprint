import unittest

from scripts.vector_index_capacity import vector_index_capacity_is_safe, vector_index_capacity_violations


class VectorIndexCapacityContractTests(unittest.TestCase):
    def test_capacity_with_headroom_passes(self):
        observations = [{"collection": "handbook", "vector_count": 700, "capacity": 1000, "shard_count": 2}]
        self.assertTrue(vector_index_capacity_is_safe(observations))

    def test_duplicate_overfull_and_invalid_observations_fail(self):
        observations = [{"collection": "handbook", "vector_count": 900, "capacity": 1000, "shard_count": 0}, {"collection": "handbook", "vector_count": -1, "capacity": 0, "shard_count": 1}]
        violations = vector_index_capacity_violations(observations)
        self.assertIn("collection_0:utilization_exceeds_budget", violations)
        self.assertIn("collection_0:shard_count_must_be_positive", violations)
        self.assertIn("collection_1:name_must_be_unique", violations)
        self.assertIn("collection_1:vector_count_must_be_non_negative", violations)
        self.assertIn("collection_1:capacity_must_be_positive", violations)


if __name__ == "__main__":
    unittest.main()
