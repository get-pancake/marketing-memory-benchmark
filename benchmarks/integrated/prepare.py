#!/usr/bin/env python3
"""Build common context packets, execute real embeddings and native GBrain.

Label files are never opened here. Every inference request is retained; no mock
vector or silent lexical fallback can substitute for an unavailable service.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from benchmarks.integrated.common import *
from analysis.separate_context import context_metrics

PIN='531b3b1ab66c88f192abb51338028c44b80fbf21'
def now():return datetime.now(timezone.utc).isoformat()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--upstream',type=Path,default=ROOT/'.cache/upstream/gbrain')
    p.add_argument('--bun',type=Path,default=ROOT/'.cache/gbrain-runtime/node_modules/@oven/bun-linux-x64/bin/bun')
    p.add_argument('--embedding-cache',type=Path,required=True)
    p.add_argument('--execute-embeddings',action='store_true')
    p.add_argument('--embedding-operational-cap-usd',type=float,default=1.0)
    p.add_argument('--workers',type=int,default=2)
    a=p.parse_args();a.upstream=a.upstream.resolve();a.bun=a.bun.resolve()
    if subprocess.check_output(['git','rev-parse','HEAD'],cwd=a.upstream,text=True).strip()!=PIN:raise ValueError('wrong upstream pin')
    if subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=a.upstream,text=True).strip():raise ValueError('upstream modified')
    data=json.loads((a.data/'inputs.json').read_text());worlds={w['id']:w for w in data['worlds']}
    a.output.mkdir(parents=True,exist_ok=False)
    texts=sorted({text_event(e) for w in data['worlds'] for e in w['events']} | {query_text(c['query'],worlds[c['query']['world']]['catalog']) for c in data['queries']})
    cache={}
    if a.embedding_cache.exists():
        for line in a.embedding_cache.read_text().splitlines():
            row=json.loads(line);cache[row['text']]=row['vector']
    missing=[s for s in texts if s not in cache]
    # Official text-embedding-3-small standard price: $0.02 / million tokens.
    # Bytes plus framing overestimate tokens. This cap is researcher-selected.
    reserved=sum(len(s.encode())+256 for s in missing)*.02/1e6
    if reserved>a.embedding_operational_cap_usd:raise ValueError('embedding operational cap exceeded')
    manifest={'created_at':now(),'data_sha256':sha((a.data/'inputs.json').read_bytes()),'upstream_pin':PIN,
        'embedding_model':'text-embedding-3-small','embedding_dimensions':1024,'embedding_price_usd_per_million':.02,
        'embedding_price_source':'https://developers.openai.com/api/docs/models/text-embedding-3-small.md',
        'embedding_operational_cap_usd':a.embedding_operational_cap_usd,'embedding_reserved_usd':reserved,
        'cap_authority':'Researcher-selected guard under explicit user authorization, not a user-specified numerical budget.',
        'source_sha256':{str(f.resolve().relative_to(ROOT)):sha(f.read_bytes()) for f in [Path(__file__),Path(__file__).with_name('common.py'),Path(__file__).with_name('gbrain-search.ts'),ROOT/'study/contract.py',ROOT/'study/retrieval.py',ROOT/'analysis/separate_context.py']},
        'status':'preparing','budgets_bytes':[1024,2048,4096,8192]}
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    if missing and not a.execute_embeddings:raise ValueError('missing real embeddings; execution flag required')
    a.embedding_cache.parent.mkdir(parents=True,exist_ok=True)
    for offset in range(0,len(missing),96):
        batch=missing[offset:offset+96];folder=a.output/f'embedding-{offset//96:04d}';folder.mkdir()
        body={'model':'text-embedding-3-small','input':batch,'dimensions':1024,'encoding_format':'float'}
        (folder/'request.json').write_text(canonical(body)+'\n')
        req=urllib.request.Request('https://api.openai.com/v1/embeddings',data=canonical(body).encode(),
            headers={'Authorization':'Bearer '+os.environ['RESEARCH_OPENAI_API_KEY'],'Content-Type':'application/json'})
        start=time.perf_counter()
        with urllib.request.urlopen(req,timeout=90) as response:raw=response.read()
        result=json.loads(raw);(folder/'response.json').write_bytes(raw)
        if len(result['data'])!=len(batch):raise ValueError('embedding count mismatch')
        for item in result['data']:
            vector=item['embedding'];norm=math.sqrt(sum(x*x for x in vector))
            if len(vector)!=1024 or not math.isfinite(norm) or norm<=0:raise ValueError('invalid real vector')
            text=batch[item['index']];cache[text]=[x/norm for x in vector]
            with a.embedding_cache.open('a') as f:f.write(canonical({'text':text,'vector':cache[text],'model':body['model']})+'\n')
        (folder/'receipt.json').write_text(json.dumps({'started_at':now(),'seconds':time.perf_counter()-start,'usage':result.get('usage'),'response_model':result.get('model')},indent=2)+'\n')
    def case_run(case):
        q=case['query'];world=worlds[q['world']];folder=a.output/case['id'];folder.mkdir()
        events=[e for e in visible(world['events'],q) if e['entity'] in ['seller',q['account']]]
        export_wiki(events,folder/'wiki')
        qt=query_text(q,world['catalog']);payload={'query':{'id':case['id'],'text':qt,'embedding':cache[qt]},
            'events':[{'id':e['id'],'text':text_event(e),'embedding':cache[text_event(e)]} for e in events]}
        env=dict(os.environ,GBRAIN_HOME=str(folder.resolve()/'gbrain-home'),RESEARCH_GBRAIN_SOURCE=str(a.upstream))
        # Native search needs no provider credentials; only common real vectors.
        for k in ['RESEARCH_OPENAI_API_KEY','RESEARCH_ANTHROPIC_API_KEY','OPENAI_API_KEY','ANTHROPIC_API_KEY']:env.pop(k,None)
        started=time.perf_counter()
        process=subprocess.run([str(a.bun),str(Path(__file__).with_name('gbrain-search.ts').resolve())],input=canonical(payload),text=True,
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,timeout=180)
        (folder/'native.stdout.json').write_text(process.stdout);(folder/'native.stderr.log').write_text(process.stderr)
        if process.returncode:raise ValueError('native GBrain failed: '+case['id'])
        native=json.loads(process.stdout)
        if not native['semantic_embedding_used'] or not native['metadata']['vector_enabled']:raise ValueError('semantic path absent')
        byid={e['id']:e for e in events};ids=[x['id'] for x in native['rankings']]
        if len(ids)!=len(set(ids)) or not set(ids)<=set(byid):raise ValueError('invalid native ranking')
        gb=[byid[i] for i in ids];generic=rank_hybrid(events,q,world['catalog'],cache)
        packets=[]
        for cap in manifest['budgets_bytes']:
            for arm in ARMS:
                evidence=select(arm,generic,gb,q,world['catalog'],cap)
                packets.append({'case_id':case['id'],'world':q['world'],'arm':arm,'budget_bytes':cap,'evidence_ids':[e['id'] for e in evidence],
                    'evidence_bytes':evidence_bytes(evidence),'messages':reader_messages(q,world['catalog'],evidence),
                    'context':context_metrics(world['events'],q,world['catalog'],[e['id'] for e in evidence])})
        (folder/'packets.json').write_text(canonical(packets)+'\n')
        receipt={'case_id':case['id'],'status':'completed','seconds':time.perf_counter()-started,'native_input_sha256':sha(canonical(payload).encode()),
            'eligible_ids':[e['id'] for e in events],'generic_ranking':[e['id'] for e in generic],'gbrain_ranking':ids}
        return receipt
    receipts=[]
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        for row in pool.map(case_run,sorted(data['queries'],key=lambda c:c['id'])):
            receipts.append(row)
            with (a.output/'attempts.jsonl').open('a') as f:f.write(canonical(row)+'\n');f.flush()
            print(canonical({'case':row['case_id'],'status':row['status'],'seconds':round(row['seconds'],2)}),flush=True)
    snapshot=a.output/'embedding-cache-snapshot.jsonl'
    snapshot.write_text(''.join(canonical({'text':s,'vector':cache[s],'model':'text-embedding-3-small'})+'\n' for s in texts))
    manifest.update(status='completed',finished_at=now(),cases=len(receipts),embedding_snapshot_sha256=sha(snapshot.read_bytes()))
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

if __name__=='__main__':main()
