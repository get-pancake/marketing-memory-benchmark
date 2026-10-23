import unittest
from prototype.summarize import summarize


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {"kind": "deterministic_development_diagnostic", "complete": False,
                         "methods": ["generic_bm25", "prompt_specialized"],
                         "planned_cases": [{"case_id": "a", "world": "one"}, {"case_id": "b", "world": "two"}]}
        self.record = {"kind": self.manifest["kind"], "case_id": "a", "world": "one",
                       "method": "generic_bm25", "status": "completed",
                       "score": {"decision_correct": True, "grounded_applicable": True, "coverage": True}}

    def test_omissions_remain_in_denominator(self):
        result = summarize(self.manifest, [self.record])
        method = result["methods"]["generic_bm25"]
        self.assertEqual(method["planned"], 2)
        self.assertEqual(method["decision_contract_correct"], 1)
        self.assertEqual(method["missing_or_interrupted"], 1)
        self.assertEqual(result["planned_attempts"], 4)

    def test_start_marker_is_not_completion(self):
        result = summarize(self.manifest, [dict(self.record, status="started")])
        self.assertEqual(result["terminal_attempts"], 0)

    def test_duplicate_terminal_attempt_rejected(self):
        with self.assertRaises(ValueError):
            summarize(self.manifest, [self.record, self.record])

    def test_mixed_actual_and_mock_evidence_rejected(self):
        with self.assertRaises(ValueError):
            summarize(self.manifest, [dict(self.record, kind="actual_model_development_pilot")])

    def test_failed_attempt_counted(self):
        result = summarize(self.manifest, [dict(self.record, status="failed", score={})])
        self.assertEqual(result["methods"]["generic_bm25"]["failed"], 1)
        self.assertEqual(result["methods"]["generic_bm25"]["decision_contract_correct"], 0)


if __name__ == "__main__":
    unittest.main()
