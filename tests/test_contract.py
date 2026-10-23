import copy
from dataclasses import replace
import unittest

from prototype.core import (Event, Query, Template, METHODS, canonical, dry_run,
                            policy_reference, retrieve, score, support_sets, visible_events)
from prototype.fixtures import build
from prototype.run import ModelClient, messages, parse_json


class ContractTests(unittest.TestCase):
    def setUp(self):
        data, labels = build()
        self.catalog = [Template(**t) for t in data["catalog"]]
        self.events = [Event(**e) for e in data["worlds"][0]["events"]]
        self.query = Query(**data["cases"][0]["query"])
        self.cases = data["cases"][:6]
        self.labels = {r["case_id"]: r for r in labels["labels"]}
        self.evidence = visible_events(self.events, self.query)
        self.alternatives = self.labels[self.cases[0]["case_id"]]["acceptable_templates"]

    def evaluate(self, output, supplied=None):
        return score(output, self.events, self.evidence if supplied is None else supplied,
                     self.query, self.catalog, self.alternatives)

    def test_fixture_cases_have_explicit_consistent_labels(self):
        for case in self.cases:
            with self.subTest(case=case["case_id"]):
                q = Query(**case["query"])
                self.assertEqual(set(support_sets(visible_events(self.events, q), q, self.catalog)),
                                 set(self.labels[case["case_id"]]["acceptable_templates"]))

    def test_unknown_future_events_cannot_change_initial_snapshot(self):
        before = [e for e in self.events if e.observed_at <= self.query.known_at]
        self.assertEqual(visible_events(before, self.query), self.evidence)

    def test_late_correction_changes_only_later_knowledge_state(self):
        initial = replace(self.query, valid_at="2026-01-02T00:00:00Z", known_at="2026-01-02T00:00:00Z")
        corrected = replace(initial, known_at="2026-01-05T00:00:00Z")
        self.assertTrue(support_sets(visible_events(self.events, initial), initial, self.catalog))
        self.assertFalse(support_sets(visible_events(self.events, corrected), corrected, self.catalog))

    def test_proposal_and_silence_do_not_become_policy(self):
        q = replace(self.query, valid_at="2026-01-02T00:00:00Z", known_at="2026-01-02T00:00:00Z")
        self.assertEqual(set(support_sets(visible_events(self.events, q), q, self.catalog)), set(self.alternatives))

    def test_access_filter_removes_proof_before_retrieval(self):
        q = replace(self.query, scopes=("sales",))
        for method in METHODS:
            selected = retrieve(self.events, q, self.catalog, method, 20000)
            self.assertFalse(any(e.relation == "proof_for_pain" for e in selected))
            self.assertFalse(support_sets(selected, q, self.catalog))

    def test_world_boundary(self):
        self.assertEqual(visible_events(self.events, replace(self.query, world="foreign")), [])

    def test_duplicate_ids_and_invalid_supersession_rejected(self):
        with self.assertRaises(ValueError):
            visible_events(self.events + [self.events[0]], self.query)
        bad = replace(self.events[1], supersedes=(self.events[0].id,), observed_at="2026-02-01T00:00:00Z")
        with self.assertRaises(ValueError):
            visible_events(self.events + [replace(bad, id="new")], self.query)

    def test_timezone_required(self):
        with self.assertRaises(ValueError):
            replace(self.query, known_at="2026-01-01")

    def test_conflicting_approved_policy_is_not_tie_broken(self):
        conflicting = replace(self.events[0], id="conflict", value="wrong_role")
        evidence = visible_events(self.events + [conflicting], self.query)
        self.assertFalse(support_sets(evidence, self.query, self.catalog))

    def test_prompt_control_receives_identical_retrieval(self):
        a = retrieve(self.events, self.query, self.catalog, "generic_bm25", 3000)
        b = retrieve(self.events, self.query, self.catalog, "prompt_specialized", 3000)
        self.assertEqual(a, b)
        self.assertEqual(messages(self.query, a, self.catalog, "generic_bm25")[1],
                         messages(self.query, b, self.catalog, "prompt_specialized")[1])

    def test_full_context_never_silently_truncates(self):
        with self.assertRaises(ValueError):
            retrieve(self.events, self.query, self.catalog, "full_context", 500)

    def test_byte_budget_is_respected_for_every_partial_method(self):
        from dataclasses import asdict
        for method in METHODS[:-1]:
            evidence = retrieve(self.events, self.query, self.catalog, method, 1500)
            self.assertLessEqual(len(canonical([asdict(e) for e in evidence]).encode()), 1500)

    def test_reference_output_and_mock_capabilities(self):
        output = policy_reference(self.evidence, self.query, self.catalog)
        result = self.evaluate(output)
        self.assertTrue(result["grounded_applicable"])
        plan = dry_run(output, result, self.catalog)
        self.assertEqual(plan["kind"], "mock_capability_dry_run")
        self.assertLessEqual(plan["units"], self.query.max_units)

    def test_multiple_acceptable_alternatives(self):
        output = policy_reference(self.evidence, self.query, self.catalog)
        output["plays"][0]["template_id"] = self.alternatives[1]
        self.assertTrue(self.evaluate(output)["grounded_applicable"])

    def test_fake_stale_or_unsupplied_citations_fail(self):
        output = policy_reference(self.evidence, self.query, self.catalog)
        output["plays"][0]["source_ids"].append("invented-source")
        self.assertIn("unavailable_citation", self.evaluate(output)["violations"])
        clean = policy_reference(self.evidence, self.query, self.catalog)
        self.assertIn("unavailable_citation", self.evaluate(clean, supplied=[])["violations"])

    def test_equivalent_source_is_accepted(self):
        duplicate = replace(self.events[0], id="equivalent-policy")
        all_events = self.events + [duplicate]
        supplied = [e for e in self.evidence if e.id != self.events[0].id] + [duplicate]
        output = policy_reference(supplied, self.query, self.catalog)
        result = score(output, all_events, supplied, self.query, self.catalog, self.alternatives)
        self.assertTrue(result["grounded_applicable"])

    def test_always_abstaining_does_not_win_positive_cases(self):
        output = {"status": "request_evidence", "account": self.query.account,
                  "objective": self.query.objective, "plays": []}
        result = self.evaluate(output)
        self.assertFalse(result["decision_correct"])
        self.assertTrue(result["inappropriate_abstention"])

    def test_missing_support_and_outreach_are_rejected(self):
        output = policy_reference(self.evidence, self.query, self.catalog)
        output["plays"][0]["source_ids"] = []
        output["plays"][0]["allowed_next_step"] = "send_outreach"
        result = self.evaluate(output)
        self.assertIn("insufficient_support", result["violations"])
        self.assertIn("action_exceeds_permission", result["violations"])

    def test_joint_resource_budget(self):
        output = policy_reference(self.evidence, replace(self.query, max_units=5), self.catalog)
        self.assertEqual(len(output["plays"]), 2)
        self.assertIn("resource_limit", self.evaluate(output)["violations"])

    def test_bad_model_shapes_are_scored_not_crashes(self):
        for obj in (None, [], "recommend", {}, {"status": [], "account": "x", "objective": "x", "plays": []}):
            with self.subTest(obj=obj):
                self.assertFalse(self.evaluate(obj)["decision_correct"])

    def test_hidden_metadata_absent_from_model_payload(self):
        payload = canonical(messages(self.query, self.evidence, self.catalog, "typed_coverage"))
        for forbidden in ("case_id", "acceptable_templates", "condition", "has_answer", "answer_session_ids"):
            self.assertNotIn(forbidden, payload)
        future = next(e for e in self.events if e.observed_at == "2026-01-05T00:00:00Z")
        self.assertNotIn(future.id, payload)

    def test_duplicate_json_keys_and_nonfinite_numbers_rejected(self):
        for text in ('{"status":"recommend","status":"request_evidence"}', '{"x":NaN}'):
            with self.assertRaises(ValueError):
                parse_json(text)

    def test_remote_model_requires_explicit_resources(self):
        with self.assertRaises(ValueError):
            ModelClient({"base_url": "https://example.com/v1", "model": "example", "max_output_tokens": 500})
        with self.assertRaises(ValueError):
            ModelClient({"base_url": "https://example.com/v1", "model": "example", "max_output_tokens": 500, "api_key": "never-store-values"})


if __name__ == "__main__":
    unittest.main()
