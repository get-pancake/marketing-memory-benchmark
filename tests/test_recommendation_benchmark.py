import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from benchmarks.recommendation.run import prepare, evaluate, case_messages, main, cost
from study.contract import applicable, slot_name, visible
from study.retrieval import aliases

ROOT=Path(__file__).resolve().parents[1]


class RecommendationPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'data/study/pilot-v5/inputs.json').read_text())
        cls.cfg=json.loads((ROOT/'benchmarks/recommendation/providers.example.json').read_text())
        cls.worlds={w['id']:w for w in cls.data['worlds']}

    def test_fixed_context_and_resource_envelope(self):
        plan=prepare(self.cfg,self.data)
        self.assertEqual(len(plan),64)
        self.assertTrue(all(r['within_input_bound'] for r in plan))
        for cid in {r['case_id'] for r in plan}:
            self.assertEqual(len({r['context_sha256'] for r in plan if r['case_id']==cid}),1)
        self.assertTrue(all(r['reserved_usd'] is None for r in plan))

    def test_correct_supported_proposals_survive_validator_after_updates(self):
        checked=0
        for case in self.data['queries']:
            w=self.worlds[case['query']['world']]
            _,events=case_messages(case,w,'direct')
            truth=applicable(visible(w['events'],case['query']),case['query'],w['catalog'])
            if not truth:continue
            tid=sorted(truth)[0];template=next(t for t in w['catalog'] if t['id']==tid)
            source_labels={v:k for k,v in aliases(events).items()}
            support={slot_name(r):None for t in w['catalog'] for r in t['requirements']}
            for req,group in zip(template['requirements'],truth[tid]):
                support[slot_name(req)]=source_labels[sorted(group)[0]]
            result=evaluate(json.dumps(dict(status='recommend',template=tid,support=support,missing=[])),case,w,events)
            self.assertTrue(result['raw_score']['decision_correct'])
            self.assertFalse(result['validator_rejected'])
            self.assertTrue(result['validated_score']['decision_correct']);checked+=1
        self.assertEqual(checked,8)

    def test_rejecting_bad_proposal_does_not_create_positive_coverage(self):
        case=next(c for c in self.data['queries'] if applicable(visible(self.worlds[c['query']['world']]['events'],c['query']),c['query'],self.worlds[c['query']['world']]['catalog']))
        w=self.worlds[case['query']['world']];_,events=case_messages(case,w,'direct')
        raw=dict(status='recommend',template=w['catalog'][0]['id'],
            support={slot_name(r):None for t in w['catalog'] for r in t['requirements']},missing=[])
        r=evaluate(json.dumps(raw),case,w,events)
        self.assertTrue(r['validator_rejected'])
        self.assertFalse(r['validated_score']['decision_correct'])
        self.assertTrue(r['validated_score']['inappropriate_abstention'])

    def test_subrequest_budget_never_contacts_provider(self):
        cfg=copy.deepcopy(self.cfg)
        for p in cfg['providers']:
            p.update(model='unit-test-snapshot',input_usd_per_million=1,output_usd_per_million=1,
                     price_source='unit test, not actual pricing',price_checked_at='2026-10-22')
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'cfg.json').write_text(json.dumps(cfg))
            argv=['runner','--config',str(p/'cfg.json'),'--output',str(p/'run'),
                  '--execute','--approved-usd-limit','0.0000001']
            with patch('sys.argv',argv),patch.dict('os.environ',{'OPENAI_API_KEY':'unit-test-not-a-key','ANTHROPIC_API_KEY':'unit-test-not-a-key'}),patch('urllib.request.urlopen') as network:
                main();network.assert_not_called()
            m=json.loads((p/'run/manifest.json').read_text())
            self.assertEqual(m['status'],'budget_exhausted')
            self.assertEqual(m['counts']['issued'],0)
            self.assertEqual(m['reserved_usd'],'0')

    def test_no_budget_cannot_execute(self):
        with tempfile.TemporaryDirectory() as tmp:
            argv=['runner','--config',str(ROOT/'benchmarks/recommendation/providers.example.json'),
                  '--output',tmp+'/run','--execute']
            with patch('sys.argv',argv),patch('urllib.request.urlopen') as network:
                with self.assertRaisesRegex(ValueError,'user-approved'):main()
                network.assert_not_called()


if __name__=='__main__':unittest.main()
