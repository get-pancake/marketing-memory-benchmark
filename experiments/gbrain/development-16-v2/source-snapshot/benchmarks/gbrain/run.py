#!/usr/bin/env python3
"""Execute and record actual GBrain component rankings and matched packet controls."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from study.contract import canonical,visible
from study.retrieval import LocalResources,query_text,text_event,retrieve,messages
from analysis.separate_context import context_metrics

PIN='531b3b1ab66c88f192abb51338028c44b80fbf21'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--upstream',type=Path,required=True)
    p.add_argument('--bun',type=Path,required=True)
    p.add_argument('--cache',type=Path,default=ROOT/'.cache/embeddings-v1.jsonl')
    p.add_argument('--token-cap',type=int,default=1024)
    a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    a.upstream=a.upstream.resolve();a.bun=a.bun.resolve()
    if subprocess.check_output(['git','rev-parse','HEAD'],cwd=a.upstream,text=True).strip()!=PIN:
        raise ValueError('upstream revision differs from protocol')
    if subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=a.upstream,text=True).strip():
        raise ValueError('upstream tracked source changed')
    data=json.loads((a.data/'inputs.json').read_text())
    worlds={w['id']:w for w in data['worlds']}
    resources=LocalResources(a.cache)
    manifest=dict(created_at=datetime.now(timezone.utc).isoformat(),status='running',
        scope='exploratory real GBrain hybrid component on existing verified-event fixtures',
        upstream_revision=PIN,bun_version=subprocess.check_output([str(a.bun),'--version'],text=True).strip(),
        data_sha256=hashlib.sha256((a.data/'inputs.json').read_bytes()).hexdigest(),
        protocol_sha256=hashlib.sha256((ROOT/'benchmarks/gbrain/protocol-v0.1.md').read_bytes()).hexdigest(),
        source_hashes={str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest()
            for x in [Path(__file__),ROOT/'benchmarks/gbrain/search.ts',ROOT/'analysis/separate_context.py',
                      ROOT/'study/contract.py',ROOT/'study/retrieval.py']},
        token_cap=a.token_cap,planned_cases=sorted(x['id'] for x in data['queries']),
        zero_generation_calls=True,raw_ingestion=False,main_market_comparison=False)
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    env=dict(os.environ,GBRAIN_HOME=str(ROOT/'.cache/gbrain-isolated'),RESEARCH_GBRAIN_SOURCE=str(a.upstream))
    outcomes=[]
    for case in sorted(data['queries'],key=lambda x:x['id']):
        q=case['query'];w=worlds[q['world']];cid=case['id'];folder=a.output/cid;folder.mkdir()
        view=[e for e in visible(w['events'],q) if e['entity'] in ['seller',q['account']]]
        qt=query_text(q,w['catalog'])
        start=time.perf_counter()
        row=dict(case_id=cid,world=q['world'],status='failed')
        try:
            # Use only saved real embeddings. Missing vectors fail; no silent
            # paid/new embedding or deterministic pseudo-vector substitution.
            def vector(text):
                key=hashlib.sha256(('qwen3-embedding-0.6b-q8_0\n'+text).encode()).hexdigest()
                return resources.cache[key]['vector']
            payload=dict(query=dict(id=cid,text=qt,embedding=vector('Instruct: Given a business research query, retrieve relevant evidence that supports its prerequisites.\nQuery: '+qt)),
                events=[dict(id=e['id'],text=text_event(e),embedding=vector(text_event(e))) for e in view])
            encoded=canonical(payload)
            (folder/'input.json').write_text(encoded+'\n')
            process=subprocess.run([str(a.bun),str(ROOT/'benchmarks/gbrain/search.ts')],input=encoded,
                env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=180)
            (folder/'stdout.json').write_text(process.stdout)
            (folder/'stderr.log').write_text(process.stderr)
            if process.returncode:raise ValueError('upstream_exit_'+str(process.returncode))
            result=json.loads(process.stdout)
            if not result['semantic_embedding_used'] or not result['metadata']['vector_enabled']:
                raise ValueError('semantic path absent')
            ids=[r['id'] for r in result['rankings']]
            if len(ids)!=len(set(ids)) or not set(ids)<={e['id'] for e in view}:
                raise ValueError('duplicate/foreign rank ID')
            byid={e['id']:e for e in view};selected=[]
            for eid in ids:
                proposed=selected+[byid[eid]]
                if resources.tokens(messages(q,w['catalog'],proposed,'prompt_hybrid'))<=a.token_cap:
                    selected=proposed
            controls={}
            for name in ['generic_hybrid','prompt_hybrid','facet_hybrid','typed']:
                evidence,receipt=retrieve(w['events'],q,w['catalog'],name,resources,a.token_cap)
                controls[name]=dict(evidence_ids=[e['id'] for e in evidence],receipt=receipt,
                    context=context_metrics(w['events'],q,w['catalog'],[e['id'] for e in evidence]))
            row.update(status='completed',ranked_pool=len(ids),eligible_pool=len(view),
                gbrain=dict(evidence_ids=[e['id'] for e in selected],timings=result['seconds'],
                    metadata=result['metadata'],input_tokens=resources.tokens(messages(q,w['catalog'],selected,'prompt_hybrid')),
                    context=context_metrics(w['events'],q,w['catalog'],[e['id'] for e in selected])),controls=controls)
        except Exception as exc:
            row.update(error_type=type(exc).__name__,error=str(exc))
        row['seconds']=time.perf_counter()-start
        with (a.output/'attempts.jsonl').open('a') as f:
            f.write(canonical(row)+'\n');f.flush();os.fsync(f.fileno())
        outcomes.append(row)
        print(json.dumps({'case':cid,'status':row['status'],'elapsed':round(row['seconds'],2)}),flush=True)
    manifest.update(status='complete',finished_at=datetime.now(timezone.utc).isoformat(),
                    completed=sum(r['status']=='completed' for r in outcomes),failed=sum(r['status']!='completed' for r in outcomes))
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

if __name__=='__main__':main()
