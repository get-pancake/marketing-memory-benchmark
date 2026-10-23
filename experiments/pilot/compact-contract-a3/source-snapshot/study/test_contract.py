"""Meaningful adversarial and metamorphic contract checks, never model results."""
import copy
import random
import unittest

from .contract import applicable,visible,sql_oracle,score
from .fixtures import build
from .retrieval import diversify
from .dryrun import execute


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data,cls.labels=build('pilot',2,1977)

    def first(self):
        w=self.data['worlds'][0];q=self.data['queries'][0]['query']
        return w,q,visible(w['events'],q)

    def test_three_way_ground_truth(self):
        # All five family contracts, including structurally checked held-out
        # families, without any model result or benchmark tuning.
        for split in ['pilot','test']:
            d,l=build(split,4,991)
            worlds={w['id']:w for w in d['worlds']}
            for c,g in zip(d['queries'],l):
                q=c['query'];w=worlds[q['world']]
                self.assertEqual(sql_oracle(w['events'],q,w['catalog']),g['acceptable'])

    def test_remove_each_support_slot(self):
        w,q,ev=self.first()
        support=applicable(ev,q,w['catalog'])['P1']
        for group in support:
            reduced=[e for e in ev if e['id'] not in group]
            self.assertFalse(applicable(reduced,q,w['catalog']))

    def test_complete_vs_incomplete_and_irrelevant_citations(self):
        w,q,ev=self.first();groups=applicable(ev,q,w['catalog'])['P1']
        ids=[sorted(g)[0] for g in groups]
        out=dict(status='recommend',plays=[dict(template='P1',evidence=ids)],missing=[])
        self.assertTrue(score(out,w['events'],ev,q,w['catalog'],['P1','P2'])['decision_correct'])
        bad=copy.deepcopy(out);bad['plays'][0]['evidence'].pop()
        self.assertIn('incomplete_support',score(bad,w['events'],ev,q,w['catalog'],['P1','P2'])['violations'])
        noise=next(e['id'] for e in ev if e['key']=='meeting_note')
        bad=copy.deepcopy(out);bad['plays'][0]['evidence'].append(noise)
        self.assertIn('irrelevant_citation',score(bad,w['events'],ev,q,w['catalog'],['P1','P2'])['violations'])

    def test_abstention_cannot_win_on_positive_cases(self):
        w,q,ev=self.first()
        s=score(dict(status='request_evidence',plays=[],missing=[]),w['events'],ev,q,w['catalog'],['P1','P2'])
        self.assertFalse(s['decision_correct']);self.assertTrue(s['inappropriate_abstention'])

    def test_future_and_permission_invariance(self):
        w,q,ev=self.first(); changed=copy.deepcopy(w['events'])
        for e in changed:
            if e['observed']>q['known_at'] or not set(e['scopes'])<=set(q['scopes']):e['value']='arbitrary unseen content'
        self.assertEqual(visible(changed,q),ev)

    def test_order_invariance(self):
        w,q,ev=self.first();events=list(w['events']);random.Random(7).shuffle(events)
        self.assertEqual(visible(events,q),ev)

    def test_duplicate_conflict_and_authority(self):
        w,q,ev=self.first()
        original=next(e for e in ev if e['key']=='approved_role')
        dupe=dict(original,id='newid')
        self.assertEqual(set(applicable(ev+[dupe],q,w['catalog'])),{'P1','P2'})
        conflict=dict(dupe,value='other')
        self.assertFalse(applicable(ev+[conflict],q,w['catalog']))
        proposal=dict(conflict,authority='proposal')
        self.assertEqual(set(applicable(ev+[proposal],q,w['catalog'])),{'P1','P2'})

    def test_budget_and_extra_play(self):
        w,q,ev=self.first();low=dict(q,max_units=1)
        self.assertFalse(applicable(ev,low,w['catalog']))
        self.assertEqual(set(applicable(ev,dict(q,max_units=2),w['catalog'])),{'P2'})

    def test_causal_correction_and_stale_ablation(self):
        w,q,_=self.first();q=dict(q,known_at=4,valid_at=4)
        self.assertEqual(set(applicable(visible(w['events'],q),q,w['catalog'])),{'P1','P2'})
        self.assertFalse(applicable(visible(w['events'],dict(q,known_at=5)),q,w['catalog']))
        self.assertGreater(len(visible(w['events'],q,True)),len(visible(w['events'],q)))

    def test_invalid_supersession(self):
        w,q,_=self.first();ev=copy.deepcopy(w['events'])
        e=next(e for e in ev if e['supersedes']);e['authority']='hypothesis'
        with self.assertRaises(ValueError):visible(ev,q)

    def test_generic_diversity_needs_no_domain_priority(self):
        events=[dict(id='a',entity='x',key='note',authority='observed'),dict(id='b',entity='x',key='note',authority='observed'),dict(id='c',entity='x',key='other',authority='observed')]
        self.assertEqual([e['id'] for e in diversify(events)],['a','c','b'])

    def test_actual_mock_dry_run_receipts(self):
        w,q,ev=self.first();groups=applicable(ev,q,w['catalog'])['P1']
        output=dict(status='recommend',plays=[dict(template='P1',evidence=[sorted(g)[0] for g in groups])],missing=[])
        spec=score(output,w['events'],ev,q,w['catalog'],['P1','P2'])['dry_run']
        result=execute(spec,ev,q,w['catalog'])
        self.assertEqual(result['units'],3);self.assertEqual(len(result['receipts']),3)
        self.assertEqual(result['kind'],'executed_mock_provider_dry_run')
        with self.assertRaises(ValueError):execute(dict(spec,steps=['send_email']),ev,q,w['catalog'])


if __name__=='__main__':unittest.main()
