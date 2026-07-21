import unittest

from scripts.citation_span_integrity import citation_span_violations, citation_spans_are_valid


class CitationSpanIntegrityTests(unittest.TestCase):
    def test_exact_source_span_passes(self):
        self.assertTrue(citation_spans_are_valid("alpha beta", [{"source_id": "doc-1", "start": 6, "end": 10, "quote": "beta"}]))

    def test_quote_mismatch_is_reported(self):
        violations = citation_span_violations("alpha beta", [{"source_id": "doc-1", "start": 6, "end": 10, "quote": "alpha"}])
        self.assertEqual(("citation_0_quote_mismatch",), violations)

    def test_out_of_bounds_span_does_not_slice_source(self):
        violations = citation_span_violations("alpha", [{"source_id": "doc-1", "start": 0, "end": 99, "quote": "alpha"}])
        self.assertEqual(("citation_0_span_out_of_bounds",), violations)


if __name__ == "__main__":
    unittest.main()
