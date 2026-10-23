#!/usr/bin/env python3
"""Recompute external QA scores from saved raw provider outputs, without inference."""
import argparse
from collections import Counter
import json
from pathlib import Path
import statistics
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from benchmarks.integrated.external_evaluate import matches,ARMS
from benchmarks.integrated.external_wiki import SOURCE,canonical,sha
from benchmarks.recommendation.run import decode
from benchmarks.integrated.run import usage_cost

def analyze(run,wiki,output):
    output.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((run/'manifest.json').read_text())
    labels={r['id']:r for r in map(json.loads,(SOURCE/'labels/agent-tasks/dev.jsonl').read_text().splitlines())}
    providers={p['provider']:p for p in manifest['config']['providers']}
    rows=[]
    for plan in manifest['planned']:
        folder=run/plan['id'];p=folder/'evaluated.json'
        row=json.loads(p.read_text()) if p.exists() else {'status':'not_attempted'}
        valid=False;correct=False;cost=0;tokens=None
        if row['status']=='completed':
            obj=json.loads((folder/'response.json').read_text())
            text,usage,_,complete=decode(plan['provider'],obj)
            answer=json.loads(text)
            correct=complete and matches(answer['answer'],labels[plan['case_id']])
            valid=all(i in plan['source_ids'] for i in answer['citations'])
            accounting=usage_cost(plan['provider'],usage,providers[plan['provider']])
            assert correct==row['answer_correct'] and valid==row['citation_ids_valid']
            assert accounting==row['accounting']
            cost=float(accounting['estimated_usd']);tokens=accounting['total_input_tokens']
        rows.append({k:plan[k] for k in ['id','case_id','provider','arm','context_bytes']} |
                    {'status':row['status'],'correct':int(correct),'citations_valid':int(valid),
                     'citations_nonempty':bool(row.get('citations')),'answer':row.get('answer'),
                     'expected':labels[plan['case_id']]['answer'],'type':labels[plan['case_id']]['answer_type'],
                     'explanation':row.get('explanation'),'seconds':row.get('seconds'),
                     'input_tokens':tokens,'estimated_usd':cost})
    groups={}
    for provider in providers:
        for arm in ARMS:
            rs=[r for r in rows if r['provider']==provider and r['arm']==arm]
            known=[r for r in rs if r['input_tokens'] is not None]
            groups[provider+'/'+arm]={'cases':len(rs),'correct':sum(r['correct'] for r in rs),
                'accuracy':sum(r['correct'] for r in rs)/len(rs),'failures':sum(r['status']!='completed' for r in rs),
                'invalid_citation_ids':sum(r['status']=='completed' and not r['citations_valid'] for r in rs),
                'empty_citations':sum(not r['citations_nonempty'] for r in rs),
                'estimated_usd':sum(r['estimated_usd'] for r in rs),
                'mean_input_tokens':statistics.mean(r['input_tokens'] for r in known) if known else None,
                'mean_context_bytes':statistics.mean(r['context_bytes'] for r in rs)}
    compilation={}
    for arm in ['wiki_generic','wiki_specialized']:
        r=json.loads((wiki/arm/'result.json').read_text())
        compilation[arm]={'status':r['status'],'bytes':len((wiki/arm/'wiki/index.md').read_bytes()),
            'estimated_usd':float(r['accounting']['estimated_usd']),'seconds':r['seconds'],
            'output_tokens':r['accounting']['output_tokens']}
    summary={'scope':'Exploratory development QA; one externally authored fictional company; no independent-company interval.',
        'run_status':manifest['status'],'planned_calls':len(rows),'completed':sum(r['status']=='completed' for r in rows),
        'attempted':sum(r['status']!='not_attempted' for r in rows),
        'groups':groups,'compilation':compilation,'estimated_reader_usd':sum(r['estimated_usd'] for r in rows),
        'citation_check':'ID validity only, not entailment or verified human assessment.',
        'source_sha256':{'run_manifest':sha((run/'manifest.json').read_bytes()),'wiki_manifest':sha((wiki/'manifest.json').read_bytes()),'analysis':sha(Path(__file__).read_bytes())}}
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (output/'per-attempt.jsonl').write_text(''.join(canonical(r)+'\n' for r in rows))
    print(canonical({'planned':len(rows),'completed':summary['completed'],'groups':groups}))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['run','wiki','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();analyze(a.run,a.wiki,a.output)
