import copy
import json
from pathlib import Path
import tempfile
import unittest

from benchmarks.integrated.common import ARMS,export_wiki,select,evidence_bytes,reader_messages
from benchmarks.integrated.run import usage_cost,reserve,planned
from benchmarks.integrated.serialization import add_format,schema_from_messages
from benchmarks.recommendation.run import evaluate
from study.fixtures import build
from study.contract import visible,applicable,slot_name,requirements,canonical
from study.retrieval import aliases

class IntegratedTests(unittest.TestCase):
    def setUp(self):
        self.data,self.labels=build('pilot',1,777)
        self.world=self.data['worlds'][0]
        self.case=self.data['queries'][0];self.q=self.case['query']
        self.events=visible(self.world['events'],self.q)
        self.cfg=json.loads(Path('benchmarks/integrated/providers.json').read_text())

    def test_no_context_never_has_sources(self):
        evidence=select('none',self.events,self.events,self.q,self.world['catalog'],2048)
        self.assertEqual(evidence,[])
        msg=reader_messages(self.q,self.world['catalog'],evidence)
        self.assertEqual(json.loads(msg[1]['content'])['evidence'],[])

    def test_all_bounded_arms_obey_exact_canonical_byte_cap(self):
        for cap in [512,1024,2048]:
            for arm in set(ARMS)-{'full','none'}:
                chosen=select(arm,self.events,self.events,self.q,self.world['catalog'],cap)
                self.assertLessEqual(evidence_bytes(chosen),cap)
                self.assertLessEqual({e['id'] for e in chosen},{e['id'] for e in self.events})

    def test_selector_does_not_filter_by_answer_values(self):
        catalog=copy.deepcopy(self.world['catalog'])
        before=select('specialized',self.events,self.events,self.q,catalog,2048)
        changed=[dict(e,value=e['value'][::-1]) for e in self.events]
        self.assertFalse(applicable(changed,self.q,catalog))
        after=select('specialized',changed,changed,self.q,catalog,2048)
        self.assertEqual([e['id'] for e in before],[e['id'] for e in after])

    def test_wiki_retains_every_permitted_source_and_no_future_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'wiki';export_wiki(self.events,path)
            text='\n'.join(p.read_text() for p in path.glob('*.md'))
            for event in self.events:self.assertIn(event['id'],text)
            for event in self.world['events']:
                if event not in self.events:self.assertNotIn(event['id'],text)

    def test_provider_cache_accounting_and_reservation(self):
        for provider in self.cfg['providers']:
            if provider['provider']=='openai':
                usage={'input_tokens':1000,'output_tokens':100,'input_tokens_details':{'cached_tokens':200,'cache_write_tokens':100}}
            else:usage={'input_tokens':700,'output_tokens':100,'cache_read_input_tokens':200,'cache_creation_input_tokens':100}
            result=usage_cost(provider['provider'],usage,provider)
            self.assertEqual(result['total_input_tokens'],1000)
            self.assertEqual(result['estimated_usd'],'0.00267')
            bound,cost=reserve(reader_messages(self.q,self.world['catalog'],self.events),provider,100)
            self.assertGreater(bound,1000);self.assertGreater(float(cost),float(result['estimated_usd']))

    def test_grounded_positive_requires_exact_bindings(self):
        truth=applicable(self.events,self.q,self.world['catalog']);tid=next(iter(truth))
        mapping={v:k for k,v in aliases(self.events).items()};catalog=self.world['catalog']
        slots={slot_name(r):None for t in catalog for r in t['requirements']}
        template=next(t for t in catalog if t['id']==tid)
        for req,group in zip(template['requirements'],truth[tid]):slots[slot_name(req)]=mapping[sorted(group)[0]]
        raw={'support':slots,'status':'recommend','template':tid,'missing':[]}
        valid=evaluate(canonical(raw),self.case,self.world,self.events)
        self.assertTrue(valid['raw_score']['supported_recommendation'])
        raw['support'][slot_name(template['requirements'][0])]=None
        invalid=evaluate(canonical(raw),self.case,self.world,self.events)
        self.assertFalse(invalid['raw_score']['supported_recommendation'])
        self.assertTrue(invalid['validator_rejected'])
        self.assertTrue(invalid['validated_score']['inappropriate_abstention'])

    def test_native_schemas_match_and_expose_only_public_options(self):
        msg=reader_messages(self.q,self.world['catalog'],self.events)
        first=add_format({},'openai',msg)['text']['format']['schema']
        second=add_format({},'anthropic',msg)['output_config']['format']['schema']
        self.assertEqual(first,second)
        self.assertEqual(set(first['properties']['support']['properties']),{slot_name(r) for t in self.world['catalog'] for r in t['requirements']})
        empty=schema_from_messages(reader_messages(self.q,self.world['catalog'],[]))
        self.assertTrue(all(v=={'type':'null'} for v in empty['properties']['support']['properties'].values()))
        self.assertEqual(len(empty['properties']['template']['anyOf'][0]['enum']),len(self.world['catalog']))

    def test_openai_cache_durations_are_not_double_counted(self):
        provider=self.cfg['providers'][0]
        usage={'input_tokens':1000,'output_tokens':100,'input_tokens_details':{
            'cached_tokens':200,'cache_write_tokens':100,
            'cache_write_tokens_details':{'ttl_30m_tokens':40,'ttl_12h_tokens':60}}}
        self.assertEqual(usage_cost('openai',usage,provider)['estimated_usd'],'0.00282')
        usage['input_tokens_details']['cache_write_tokens_details']['ttl_30m_tokens']=50
        with self.assertRaises(ValueError):usage_cost('openai',usage,provider)

if __name__=='__main__':unittest.main()
