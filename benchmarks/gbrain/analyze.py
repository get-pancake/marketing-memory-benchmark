#!/usr/bin/env python3
"""Score saved real GBrain rankings; add a disclosed same-backend coverage control."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import statistics
import sys

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from study.contract import visible,requirements,canonical
from study.retrieval import LocalResources,messages,diversify,retrieve
from analysis.separate_context import context_metrics
from analysis.analyze_study import paired_ci

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',type=Path,required=True);p.add_argument('--data',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--token-cap',type=int)
    p.add_argument('--offline-token-counts',type=Path,
                   help='Rebuild packets from saved actual tokenizer counts; no local model service needed')
    p.add_argument('--cache',type=Path,default=ROOT/'.cache/embeddings-v1.jsonl');a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((a.run/'manifest.json').read_text())
    if manifest['status']!='complete':raise ValueError('source run incomplete')
    data=json.loads((a.data/'inputs.json').read_text())
    if hashlib.sha256((a.data/'inputs.json').read_bytes()).hexdigest()!=manifest['data_sha256']:
        raise ValueError('source data changed')
    worlds={w['id']:w for w in data['worlds']};queries={q['id']:q['query'] for q in data['queries']}
    rs=[json.loads(x) for x in (a.run/'attempts.jsonl').read_text().splitlines()]
    if sorted(r['case_id'] for r in rs)!=manifest['planned_cases']:raise ValueError('case denominator mismatch')
    resources=LocalResources(a.cache);rows=[]
    runtime_hash=hashlib.sha256((ROOT/'experiments/qwen3-moe-runtime.json').read_bytes()).hexdigest()
    if a.offline_token_counts:
        token_receipt=json.loads(a.offline_token_counts.read_text())
        if token_receipt['runtime_manifest_sha256']!=runtime_hash:raise ValueError('tokenizer runtime identity changed')
        def recorded_tokens(msg):
            key=hashlib.sha256(canonical(msg).encode()).hexdigest()
            count=token_receipt['counts'][key]
            if not isinstance(count,int) or count<1:raise ValueError('invalid token count receipt')
            resources.token_cache[key]=count
            return count
        resources.tokens=recorded_tokens
        embedding=resources.embedding
        def recorded_embedding(text,kind):
            key=hashlib.sha256(('qwen3-embedding-0.6b-q8_0\n'+text).encode()).hexdigest()
            if key not in resources.cache:raise ValueError('offline embedding receipt missing')
            return embedding(text,kind)
        resources.embedding=recorded_embedding
    cap=a.token_cap or manifest['token_cap']
    for r in rs:
        q=queries[r['case_id']];w=worlds[q['world']]
        current=visible(w['events'],q);byid={e['id']:e for e in current}
        if r['status']=='completed':
            ranked=json.loads((a.run/r['case_id']/'stdout.json').read_text())['rankings']
            needed={k for t in w['catalog'] if t['objective']==q['objective'] and t['units']<=q['max_units']
                    for k in requirements(t,q)}
            candidates=diversify([byid[e['id']] for e in ranked],needed);selected=[]
            for e in candidates:
                proposed=selected+[e]
                if resources.tokens(messages(q,w['catalog'],proposed,'prompt_hybrid'))<=cap:
                    selected=proposed
            control=context_metrics(w['events'],q,w['catalog'],[e['id'] for e in selected])
            results={'gbrain_hybrid':r['gbrain'],'gbrain_catalog_coverage':dict(context=control,evidence_ids=[e['id'] for e in selected]),**r['controls']}
            if cap!=manifest['token_cap']:
                plain=[]
                for item in ranked:
                    proposed=plain+[byid[item['id']]]
                    if resources.tokens(messages(q,w['catalog'],proposed,'prompt_hybrid'))<=cap:plain=proposed
                results['gbrain_hybrid']=dict(evidence_ids=[e['id'] for e in plain],
                    context=context_metrics(w['events'],q,w['catalog'],[e['id'] for e in plain]))
                for name in ['generic_hybrid','prompt_hybrid','facet_hybrid','typed']:
                    evidence,receipt=retrieve(w['events'],q,w['catalog'],name,resources,cap)
                    results[name]=dict(evidence_ids=[e['id'] for e in evidence],receipt=receipt,
                        context=context_metrics(w['events'],q,w['catalog'],[e['id'] for e in evidence]))
        else:
            results={name:dict(context=context_metrics(w['events'],q,w['catalog'],[]),evidence_ids=[])
                     for name in ['gbrain_hybrid','gbrain_catalog_coverage','generic_hybrid','prompt_hybrid','facet_hybrid','typed']}
        for name,result in results.items():
            evidence=[byid[eid] for eid in result['evidence_ids']]
            token_count=resources.tokens(messages(q,w['catalog'],evidence,
                'generic_hybrid' if name=='generic_hybrid' else 'prompt_hybrid'))
            rows.append(dict(case_id=r['case_id'],world=q['world'],family=w['family'],method=name,
                status=r['status'],evidence_ids=result['evidence_ids'],packed_input_tokens=token_count,**result['context']))
    summaries={};world_means={};families={w['id']:w['family'] for w in worlds.values()}
    for name in sorted({r['method'] for r in rows}):
        mr=[r for r in rows if r['method']==name];pos=[r for r in mr if r['answerable']]
        grouped=defaultdict(list)
        for r in pos:grouped[r['world']].append(int(r['complete_positive_support']))
        world_means[name]={w:statistics.mean(v) for w,v in grouped.items()}
        summaries[name]=dict(cases=len(mr),positive_cases=len(pos),
            complete_positive_support=sum(r['complete_positive_support'] for r in pos),
            complete_positive_rate=statistics.mean(r['complete_positive_support'] for r in pos),
            mean_current_value_group_coverage=statistics.mean(r['current_value_group_coverage'] for r in mr if r['current_value_group_coverage'] is not None),
            false_affordance_cases=sum(r['false_affordance'] for r in mr),
            mean_packed_input_tokens=statistics.mean(r['packed_input_tokens'] for r in mr),
            failures=sum(r['status']!='completed' for r in mr))
    contrasts={}
    for left,right in [('typed','gbrain_hybrid'),('typed','gbrain_catalog_coverage'),('gbrain_catalog_coverage','gbrain_hybrid')]:
        values={w:world_means[left][w]-world_means[right][w] for w in world_means[left]}
        contrasts[left+' minus '+right]=dict(mean=statistics.mean(values.values()),
            descriptive_world_ci95=paired_ci(values,families),independent_worlds=len(values))
    result=dict(scope='exploratory controlled component comparison; all v1 cases were already available',
        source_attempts_sha256=hashlib.sha256((a.run/'attempts.jsonl').read_bytes()).hexdigest(),
        upstream_revision=manifest['upstream_revision'],token_cap=cap,methods=summaries,contrasts=contrasts,
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        added_control='gbrain_catalog_coverage reorders the saved real GBrain pool with the same public prerequisite-coverage module; no new native query is counted',
        limits=['Not full raw ingestion, default hosted GBrain, graph extraction or paid reranking.',
                'Every system receives verified typed facts and a shared correct temporal/access view.',
                'Coverage is not decision utility, strategic quality, revenue or evidence that GBrain must be replaced.'])
    (a.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    (a.output/'per-query.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows))
    (a.output/'token-counts.json').write_text(json.dumps(dict(runtime_manifest_sha256=runtime_hash,
        source='Saved actual local apply-template/tokenize counts for the pinned reader; not model generation.',
        counts=resources.token_cache),sort_keys=True,indent=2)+'\n')
    print(json.dumps({'methods':summaries,'contrasts':contrasts}))

if __name__=='__main__':main()
