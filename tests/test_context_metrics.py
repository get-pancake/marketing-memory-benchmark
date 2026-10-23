"""Adversarial checks for context sufficiency, separate from model quality."""
import copy
import unittest

from analysis.separate_context import context_metrics
from study.contract import applicable, visible
from study.fixtures import build


class ContextMetricsTests(unittest.TestCase):
    def setUp(self):
        data, _ = build('pilot', 2, 1977)
        self.world = data['worlds'][0]
        self.query = data['queries'][0]['query']
        self.events = self.world['events']
        self.catalog = self.world['catalog']
        self.current = visible(self.events, self.query)
        self.groups = next(iter(applicable(self.current, self.query, self.catalog).values()))
        self.support = [sorted(group)[0] for group in self.groups]

    def metric(self, ids, events=None):
        return context_metrics(self.events if events is None else events,
                               self.query, self.catalog, ids)

    def test_complete_evidence_and_missing_prerequisite(self):
        self.assertTrue(self.metric(self.support)['complete_positive_support'])
        for source in self.support:
            self.assertFalse(self.metric([i for i in self.support if i != source])['complete_positive_support'])

    def test_conflict_omission_creates_false_affordance(self):
        original = next(e for e in self.current if e['key'] == 'approved_role')
        conflicting = dict(copy.deepcopy(original), id='conflicting-policy', value='other-role')
        result = self.metric(self.support, self.events + [conflicting])
        self.assertFalse(result['answerable'])
        self.assertTrue(result['false_affordance'])
        self.assertFalse(result['all_current_value_groups_available'])
        both = self.metric(self.support + ['conflicting-policy'], self.events + [conflicting])
        self.assertFalse(both['false_affordance'])

    def test_unauthorized_evidence_is_counted_but_cannot_supply_support(self):
        original = next(e for e in self.current if e['id'] == self.support[0])
        private = dict(copy.deepcopy(original), id='restricted-copy', scopes=['never-permitted'])
        result = self.metric(self.support[1:] + ['restricted-copy'], self.events + [private])
        self.assertEqual(result['stale_or_ineligible_sources'], 1)
        self.assertFalse(result['complete_positive_support'])

    def test_unknown_and_duplicate_source_ids_fail(self):
        with self.assertRaisesRegex(ValueError, 'unknown'):
            self.metric(['fabricated-source'])
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.metric([self.support[0], self.support[0]])


if __name__ == '__main__':
    unittest.main()
