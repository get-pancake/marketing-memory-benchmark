"""Meaningful adversarial and metamorphic contract checks, never model results."""
import copy
import random
import unittest

from .contract import applicable,visible,sql_oracle,score
from .fixtures import build
from .retrieval import diversify, aliases, bind_output, messages, output_schema
from .dryrun import execute


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data,cls.labels=build('pilot',2,1977)

    def first(self):
        w=self.data['worlds'][0];q=self.data['queries'][0]['query']
        return w,q,visible(w['events'],q)

    def choice(self,w,q,ev):
        truth=applicable(ev,q,w['catalog'])
        tid=sorted(truth)[0]
        return tid,truth[tid],sorted(truth)

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
        _,support,_=self.choice(w,q,ev)
        for group in support:
            reduced=[e for e in ev if e['id'] not in group]
            self.assertFalse(applicable(reduced,q,w['catalog']))

    def test_complete_vs_incomplete_and_irrelevant_citations(self):
        w,q,ev=self.first();tid,groups,gold=self.choice(w,q,ev)
        ids=[sorted(g)[0] for g in groups]
        out=dict(status='recommend',plays=[dict(template=tid,evidence=ids)],missing=[])
        self.assertTrue(score(out,w['events'],ev,q,w['catalog'],gold)['decision_correct'])
        bad=copy.deepcopy(out);bad['plays'][0]['evidence'].pop()
        self.assertIn('incomplete_support',score(bad,w['events'],ev,q,w['catalog'],gold)['violations'])
        noise=next(e['id'] for e in ev if e['id'] not in set.union(*groups))
        bad=copy.deepcopy(out);bad['plays'][0]['evidence'].append(noise)
        self.assertIn('irrelevant_citation',score(bad,w['events'],ev,q,w['catalog'],gold)['violations'])

    def test_abstention_cannot_win_on_positive_cases(self):
        w,q,ev=self.first()
        s=score(dict(status='request_evidence',plays=[],missing=[]),w['events'],ev,q,w['catalog'],sorted(applicable(ev,q,w['catalog'])))
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
        self.assertEqual(set(applicable(ev+[dupe],q,w['catalog'])),set(applicable(ev,q,w['catalog'])))
        conflict=dict(dupe,value='other')
        self.assertFalse(applicable(ev+[conflict],q,w['catalog']))
        proposal=dict(conflict,authority='proposal')
        self.assertEqual(set(applicable(ev+[proposal],q,w['catalog'])),set(applicable(ev,q,w['catalog'])))

    def test_budget_and_extra_play(self):
        w,q,ev=self.first();low=dict(q,max_units=1)
        self.assertFalse(applicable(ev,low,w['catalog']))
        self.assertEqual(len(applicable(ev,dict(q,max_units=2),w['catalog'])),1)

    def test_causal_correction_and_stale_ablation(self):
        w,_,_=self.first();q=self.data['queries'][3]['query'];later=self.data['queries'][4]['query']
        self.assertTrue(applicable(visible(w['events'],q),q,w['catalog']))
        self.assertFalse(applicable(visible(w['events'],later),later,w['catalog']))
        self.assertGreater(len(visible(w['events'],q,True)),len(visible(w['events'],q)))

    def test_invalid_supersession(self):
        w,q,_=self.first();ev=copy.deepcopy(w['events'])
        e=next(e for e in ev if e['supersedes']);e['authority']='hypothesis'
        with self.assertRaises(ValueError):visible(ev,q)

    def test_late_correction_changes_same_valid_time_only_when_observed(self):
        w,_,_=self.first();before=self.data['queries'][3]['query'];after=self.data['queries'][4]['query']
        self.assertEqual(before['valid_at'],after['valid_at'])
        self.assertLess(before['known_at'],after['known_at'])
        self.assertTrue(sql_oracle(w['events'],before,w['catalog']))
        self.assertFalse(sql_oracle(w['events'],after,w['catalog']))

    def test_generic_diversity_needs_no_domain_priority(self):
        events=[dict(id='a',entity='x',key='note',authority='observed'),dict(id='b',entity='x',key='note',authority='observed'),dict(id='c',entity='x',key='other',authority='observed')]
        self.assertEqual([e['id'] for e in diversify(events)],['a','c','b'])

    def test_actual_mock_dry_run_receipts(self):
        w,q,ev=self.first();tid,groups,gold=self.choice(w,q,ev)
        output=dict(status='recommend',plays=[dict(template=tid,evidence=[sorted(g)[0] for g in groups])],missing=[])
        spec=score(output,w['events'],ev,q,w['catalog'],gold)['dry_run']
        result=execute(spec,ev,q,w['catalog'])
        self.assertEqual(result['units'],spec['units']);self.assertEqual(len(result['receipts']),spec['units'])
        self.assertEqual(result['kind'],'executed_mock_provider_dry_run')
        with self.assertRaises(ValueError):execute(dict(spec,steps=['send_email']),ev,q,w['catalog'])

    def test_source_bindings_do_not_choose_correct_evidence(self):
        w,q,ev=self.first();tid,groups,gold=self.choice(w,q,ev)
        mapping=aliases(ev);reverse={v:k for k,v in mapping.items()}
        raw=dict(status='recommend',plays=[dict(template=tid,evidence=[reverse[sorted(g)[0]] for g in groups])],missing=[])
        self.assertTrue(score(bind_output(raw,ev),w['events'],ev,q,w['catalog'],gold)['decision_correct'])
        raw['plays'][0]['evidence']=['S1']
        self.assertFalse(score(bind_output(raw,ev),w['events'],ev,q,w['catalog'],gold)['decision_correct'])
        raw['plays'][0]['evidence']=['invented']
        with self.assertRaises(ValueError):bind_output(raw,ev)
        self.assertEqual(messages(q,w['catalog'],ev,'typed'),messages(q,w['catalog'],list(reversed(ev)),'typed'))
        schema=output_schema(w['catalog'],ev)['json_schema']['schema']['oneOf'][0]
        self.assertEqual(set(schema['properties']['plays']['items']['properties']['template']['enum']),{t['id'] for t in w['catalog']})


if __name__=='__main__':unittest.main()
