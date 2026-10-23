"""Fault-injection checks using artificial ledger entries, not model outputs."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from .ledger import recover,atomic_json


class RecoveryTests(unittest.TestCase):
    def test_torn_append_preserved_and_pending_call_not_lost(self):
        plan=[dict(attempt_id=i,case_id='c'+str(i),world='w',method='m') for i in range(3)]
        records=[dict(plan[0],status='started'),dict(plan[0],status='completed'),
                 dict(plan[1],status='started'),dict(plan[1],status='model_call_started')]
        prefix=''.join(json.dumps(r)+'\n' for r in records).encode();tail=b'{"attempt_id":1,"status":"com'
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'attempts.jsonl';p.write_bytes(prefix+tail)
            done,pending,repairs=recover(p,plan)
            self.assertEqual(done,{0});self.assertEqual([r['attempt_id'] for r in pending],[1])
            self.assertEqual(p.read_bytes(),prefix)
            self.assertEqual((p.parent/repairs[0]['path']).read_bytes(),tail)
            # Attempt 2 never started, so it alone is eligible for fresh work.
            self.assertEqual({r['attempt_id'] for r in plan}-done-{r['attempt_id'] for r in pending},{2})

    def test_complete_corruption_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'attempts.jsonl';p.write_bytes(b'{broken}\n')
            with self.assertRaisesRegex(ValueError,'corrupt complete'):recover(p,[])

    def test_terminal_cannot_be_repeated_or_reopened(self):
        plan=[dict(attempt_id=0,case_id='c',world='w',method='m')]
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'attempts.jsonl'
            p.write_text(json.dumps(dict(plan[0],status='completed'))+'\n'+json.dumps(dict(plan[0],status='started'))+'\n')
            with self.assertRaisesRegex(ValueError,'after terminal'):recover(p,plan)

    def test_atomic_manifest_and_valid_final_line(self):
        plan=[dict(attempt_id=0,case_id='c',world='w',method='m')]
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);atomic_json(root/'manifest.json',{'complete':False})
            self.assertEqual(json.loads((root/'manifest.json').read_text()),{'complete':False})
            p=root/'attempts.jsonl';p.write_text(json.dumps(dict(plan[0],status='completed')))
            done,pending,repairs=recover(p,plan)
            self.assertEqual(done,{0});self.assertFalse(pending);self.assertTrue(p.read_bytes().endswith(b'\n'))

    def test_runner_resumes_only_unstarted_work(self):
        # Explicit unit-test stand-ins, kept only in a disposable directory.
        # No endpoint is contacted and these records are never experiment data.
        import argparse,contextlib,hashlib,io
        from .fixtures import build
        from .contract import canonical,visible
        from .run import run
        calls=[]
        class UnitClient:
            local=True
            def __init__(self,config):pass
            def reserve(self,messages):pass
            def request_json(self,messages,response_format=None):
                return json.dumps(dict(messages=messages,response_format=response_format),separators=(',',':'))
            def complete(self,messages,response_format=None):
                calls.append(messages)
                if len(calls)==2:raise KeyboardInterrupt('injected interruption')
                properties=response_format['json_schema']['schema']['oneOf'][0]['properties']['support']['properties']
                raw=dict(support={k:None for k in properties},status='request_evidence',template=None,missing=[])
                return dict(raw_output=canonical(raw),request_json=self.request_json(messages,response_format),
                    usage={'prompt_tokens':10,'completion_tokens':1},finish_reason='stop')
        def unit_retrieve(events,q,catalog,method,resources,cap):
            return visible(events,q),dict(prompt_tokens=10,seconds=0,embedding_receipts=[])
        with tempfile.TemporaryDirectory() as tmp,contextlib.redirect_stdout(io.StringIO()):
            root=Path(tmp);data=root/'data';data.mkdir();inputs,labels=build('pilot',1,312)
            hashes={}
            for name,value in [('inputs.json',inputs),('labels.json',labels)]:
                p=data/name;p.write_text(canonical(value)+'\n');hashes[name]=hashlib.sha256(p.read_bytes()).hexdigest()
            atomic_json(data/'manifest.json',dict(split='pilot',files=hashes))
            config=root/'config.json';atomic_json(config,dict(model='unit-test',base_url='http://127.0.0.1:1/v1'))
            runtime=root/'runtime.json';atomic_json(runtime,dict(model='unit-test',model_sha256='unit-test-only'))
            args=argparse.Namespace(data=data,output=root/'run',model_config=config,runtime_manifest=runtime,
                freeze=None,methods=['typed'],token_cap=1024,order_seed=1,conditions=['initial','policy_revision','objective_change'],
                embedding_cache=root/'cache.jsonl',resume=False)
            with patch('study.run.ModelClient',UnitClient),patch('study.run.retrieve',unit_retrieve):
                with self.assertRaises(KeyboardInterrupt):run(args)
                self.assertFalse(json.loads((args.output/'manifest.json').read_text())['complete'])
                args.resume=True;run(args)
            rows=[json.loads(line) for line in (args.output/'attempts.jsonl').read_text().splitlines()]
            terminal=[r for r in rows if r['status'] in ['completed','failed']]
            self.assertEqual(len(calls),3)
            self.assertEqual([r['attempt_id'] for r in terminal],[0,1,2])
            self.assertEqual(terminal[1]['error_type'],'Interrupted')
            self.assertTrue(json.loads((args.output/'manifest.json').read_text())['complete'])
            calls.clear();args.output=root/'cached-run';args.resume=False;args.reuse_identical=True
            args.conditions=['initial'];args.methods=['typed','full_context','typed_history']
            with patch('study.run.ModelClient',UnitClient),patch('study.run.retrieve',unit_retrieve):run(args)
            cached=[json.loads(line) for line in (args.output/'attempts.jsonl').read_text().splitlines()]
            self.assertEqual(len(calls),1)
            self.assertEqual(sum(r['status']=='model_call_reused' for r in cached),2)
            finished=[r for r in cached if r['status']=='completed']
            self.assertEqual(len(finished),3)
            # All three are incorrect on a positive case: failures are reused too.
            self.assertTrue(all(not r['score']['decision_correct'] for r in finished))


if __name__=='__main__':unittest.main()
