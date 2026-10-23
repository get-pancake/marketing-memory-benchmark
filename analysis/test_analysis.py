"""Accounting checks with explicitly artificial, ephemeral records; no inference."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from analysis.analyze_study import analyze, paired_ci
from study.contract import applicable, canonical, score, visible
from study.fixtures import build


class AccountingTest(unittest.TestCase):
    def fixture(self, root):
        import hashlib
        data,labels=build('pilot',2,971)
        dataset=root/'data';dataset.mkdir()
        hashes={}
        for name,value in [('inputs.json',data),('labels.json',labels)]:
            path=dataset/name;path.write_text(canonical(value)+'\n')
            hashes[name]=hashlib.sha256(path.read_bytes()).hexdigest()
        worlds={w['id']:w for w in data['worlds']}
        run=root/'run';run.mkdir();plan=[];terminal=[]
        for case,label in zip(data['queries'],labels):
            q=case['query'];w=worlds[q['world']];ev=visible(w['events'],q)
            truth=applicable(ev,q,w['catalog'])
            output={'status':'request_evidence','plays':[],'missing':[]}
            if truth:
                tid=sorted(truth)[0]
                output={'status':'recommend','plays':[{'template':tid,'evidence':[sorted(g)[0] for g in truth[tid]]}],'missing':[]}
            for method in ['prompt_hybrid','typed']:
                row=dict(attempt_id=len(plan),method=method,world=q['world'],case_id=case['id'])
                plan.append(row)
                terminal.append(dict(row,status='completed',output=output,evidence_ids=[e['id'] for e in ev],
                    score=score(output,w['events'],ev,q,w['catalog'],label['acceptable'])))
        # A post-score execution failure must not count as primary success.
        terminal[1]['status']='failed'
        # A missing attempt must not disappear from the denominator.
        terminal=[r for r in terminal if r['attempt_id']!=3]
        (run/'manifest.json').write_text(json.dumps(dict(complete=False,planned=plan,dataset_manifest={'files':hashes})))
        (run/'attempts.jsonl').write_text(''.join(canonical(r)+'\n' for r in terminal))
        return run,dataset

    def test_missing_and_failed_count_and_pair_by_world(self):
        with tempfile.TemporaryDirectory() as tmp,contextlib.redirect_stdout(io.StringIO()):
            root=Path(tmp);run,data=self.fixture(root)
            result=analyze(run,data,root/'analysis')
        self.assertEqual(result['planned_attempts'],32)
        self.assertEqual(result['recorded_terminal_attempts'],31)
        self.assertEqual(result['methods']['typed']['primary'],14/16)
        self.assertEqual(result['methods']['typed']['failures'],2)
        contrast=result['paired_contrasts']['typed minus prompt_hybrid']
        self.assertEqual(contrast['mean'],-.125)
        self.assertEqual(sorted(contrast['world_differences'].values()),[-.25,0])
        self.assertIsNone(contrast['ci95'])

    def test_duplicate_terminal_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);run,data=self.fixture(root)
            ledger=run/'attempts.jsonl'
            with ledger.open('a') as f:f.write(ledger.read_text().splitlines()[0]+'\n')
            with self.assertRaisesRegex(ValueError,'duplicate terminal'):
                analyze(run,data,root/'analysis')

    def test_stratification_preserves_fixed_family_mix(self):
        values={str(i):(0 if i<3 else 1) for i in range(6)}
        families={str(i):('a' if i<3 else 'b') for i in range(6)}
        self.assertEqual(paired_ci(values,families,draws=100),[.5,.5])


if __name__=='__main__':unittest.main()
