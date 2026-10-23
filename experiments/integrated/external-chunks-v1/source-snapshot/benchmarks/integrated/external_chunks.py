#!/usr/bin/env python3
"""Post-hoc development robustness control: ordinary chunked BM25, same reader."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
import json
from pathlib import Path
import random
import statistics
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from benchmarks.integrated.external_evaluate import SYSTEM,SCHEMA,matches,bm25
from benchmarks.integrated.external_wiki import ROOT,SOURCE,corpus,render,call,now,canonical,sha
from benchmarks.recommendation.run import payload,decode
from benchmarks.integrated.run import usage_cost

def chunks(docs):
    result=[]
    # Fixed ordinary character windows, chosen before these reader calls.
    # Overlap preserves boundary-spanning clauses. No answer/evidence-slug input.
    for d in docs:
        for i,start in enumerate(range(0,len(d['text']),1792)):
            result.append(dict(d,slug=d['slug']+f' / fragment {i+1}',text=d['text'][start:start+2048]))
    return result

def execute(output,cap,do_execute):
    cfg=json.loads((ROOT/'benchmarks/integrated/providers.json').read_text());docs=chunks(corpus())
    labels={r['id']:r for r in map(json.loads,(SOURCE/'labels/agent-tasks/dev.jsonl').read_text().splitlines())}
    plans=[]
    for q in labels.values():
        selected=bm25(q['question'],docs,24576);context=render(selected)
        messages=[{'role':'system','content':SYSTEM},{'role':'user','content':canonical({'question':q['question'],'company_context':context})}]
        for provider in cfg['providers']:
            body=payload(provider,messages,2048)
            if provider['provider']=='openai':body['text']={'format':{'type':'json_schema','name':'company_answer','strict':True,'schema':SCHEMA}}
            else:body['output_config']={'format':{'type':'json_schema','schema':SCHEMA}}
            plans.append({'id':q['id']+'-'+provider['provider']+'-raw_chunks','case_id':q['id'],'provider':provider['provider'],
                'arm':'raw_chunks','body':body,'context_bytes':len(context.encode()),'source_ids':sorted({d['id'] for d in selected}),
                'reserved_usd':(len(canonical(body).encode())+4096)*5/1e6+2048*10/1e6})
    random.Random(2026102304).shuffle(plans)
    reserved=sum(p['reserved_usd'] for p in plans)
    if reserved>cap:raise ValueError('operational cap too small')
    output.mkdir(parents=True,exist_ok=False)
    manifest={'created_at':now(),'status':'running' if do_execute else 'planned','config':cfg,'planned':plans,
        'post_hoc_development_control':True,'reason':'Original whole-document packer cannot include a 58,320-byte contract within24,576bytes.',
        'chunk_chars':2048,'overlap_chars':256,'evidence_cap_bytes':24576,'reserved_usd':reserved,'operational_cap_usd':cap,
        'source_sha256':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [Path(__file__).resolve(),ROOT/'benchmarks/integrated/external_evaluate.py',ROOT/'benchmarks/integrated/external_wiki.py']}}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    for path in manifest['source_sha256']:
        target=output/'source-snapshot'/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/path).read_bytes())
    print(canonical({'planned':len(plans),'reserved_usd':reserved,'executed':do_execute}),flush=True)
    if not do_execute:return
    providers={p['provider']:p for p in cfg['providers']};rows=[]
    def one(plan):
        row=call(providers[plan['provider']],plan['body'],output/plan['id'])
        row.update({k:plan[k] for k in ['id','case_id','arm','context_bytes']});row['answer_correct']=False
        if row['status']=='completed':
            try:
                parsed=json.loads(row['text']);row.update(parsed)
                row['answer_correct']=matches(parsed['answer'],labels[plan['case_id']])
                row['citation_ids_valid']=all(x in plan['source_ids'] for x in parsed['citations'])
            except Exception as e:row.update(status='failed',error_type=type(e).__name__)
        (output/plan['id']/'evaluated.json').write_text(json.dumps(row,indent=2)+'\n')
        return row
    with ThreadPoolExecutor(max_workers=12) as pool:
        for offset in range(0,len(plans),12):
            wave=plans[offset:offset+12]
            with (output/'attempts.jsonl').open('a') as f:
                for p in wave:f.write(canonical({'id':p['id'],'status':'issued','at':now()})+'\n')
            stop=False
            for future in as_completed([pool.submit(one,p) for p in wave]):
                row=future.result();rows.append(row)
                with (output/'attempts.jsonl').open('a') as f:f.write(canonical(row)+'\n')
                stop|=row.get('http_status') in [401,403,429]
            if stop:manifest['status']='provider_stop';break
        else:manifest['status']='completed'
    manifest.update(attempted=len(rows),finished_at=now())
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

def analyze(run,output):
    manifest=json.loads((run/'manifest.json').read_text());providers={p['provider']:p for p in manifest['config']['providers']}
    labels={r['id']:r for r in map(json.loads,(SOURCE/'labels/agent-tasks/dev.jsonl').read_text().splitlines())};rows=[]
    for plan in manifest['planned']:
        row=json.loads((run/plan['id']/'evaluated.json').read_text())
        if row['status']=='completed':
            obj=json.loads((run/plan['id']/'response.json').read_text());text,usage,_,complete=decode(plan['provider'],obj)
            assert complete and matches(json.loads(text)['answer'],labels[plan['case_id']])==row['answer_correct']
            assert usage_cost(plan['provider'],usage,providers[plan['provider']])==row['accounting']
        rows.append(row)
    groups={}
    for provider in providers:
        rs=[r for r in rows if r['provider']==provider]
        groups[provider+'/raw_chunks']={'cases':len(rs),'correct':sum(r['answer_correct'] for r in rs),
            'failures':sum(r['status']!='completed' for r in rs),'estimated_usd':sum(float(r.get('accounting',{}).get('estimated_usd',0)) for r in rs),
            'mean_context_bytes':statistics.mean(r['context_bytes'] for r in rs),
            'mean_input_tokens':statistics.mean(r['accounting']['total_input_tokens'] for r in rs if r.get('accounting'))}
    output.mkdir(parents=True,exist_ok=False)
    (output/'summary.json').write_text(json.dumps({'post_hoc_development_control':True,'run_status':manifest['status'],
        'planned_calls':len(rows),'groups':groups,'manifest_sha256':sha((run/'manifest.json').read_bytes())},indent=2)+'\n')
    (output/'per-attempt.jsonl').write_text(''.join(canonical(r)+'\n' for r in rows))
    print(canonical(groups))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--execute',action='store_true');p.add_argument('--analyze',type=Path)
    p.add_argument('--operational-cap-usd',type=float,default=10)
    a=p.parse_args()
    if a.analyze:analyze(a.analyze,a.output)
    else:execute(a.output,a.operational_cap_usd,a.execute)
