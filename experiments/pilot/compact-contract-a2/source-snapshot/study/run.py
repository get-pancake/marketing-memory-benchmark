"""Execute a saved paired plan; actual model calls never fall back to mocks."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import time

from prototype.run import ModelClient, parse_json, git
from .contract import canonical, applicable, visible, sql_oracle, score
from .retrieval import METHODS, LocalResources, messages, retrieve
from .dryrun import execute

ROOT=Path(__file__).resolve().parents[1]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()


def source_hashes():
    files=list((ROOT/'study').glob('*.py'))+[ROOT/'prototype/run.py',ROOT/'prototype/core.py']
    return {str(p.relative_to(ROOT)):sha(p) for p in sorted(files)}


def run(args):
    dataset=json.loads((args.data/'manifest.json').read_text())
    for name,digest in dataset['files'].items():
        if sha(args.data/name)!=digest:raise ValueError('dataset hash mismatch')
    data=json.loads((args.data/'inputs.json').read_text())
    labels={r['id']:r for r in json.loads((args.data/'labels.json').read_text())}
    worlds={w['id']:w for w in data['worlds']}
    cases={c['id']:c['query'] for c in data['queries']}
    code=source_hashes()
    config=json.loads(args.model_config.read_text())
    client=ModelClient(config)
    if not client.local:raise ValueError('This frozen study currently supports only the audited local configuration')
    freeze=json.loads(args.freeze.read_text()) if args.freeze else None
    if dataset['split']=='test':
        if not freeze or freeze['source_sha256']!=code or freeze['dataset_files']!=dataset['files']:
            raise ValueError('test requires matching frozen code and data')
        if (freeze['model_config']!=config or freeze['methods']!=args.methods or
            freeze['token_cap']!=args.token_cap or freeze['order_seed']!=args.order_seed or args.conditions):
            raise ValueError('frozen settings differ from request')
    # Every world/query has an independently checked deterministic construction label.
    for cid,q in cases.items():
        w=worlds[q['world']]
        if sorted(labels[cid]['acceptable'])!=sql_oracle(w['events'],q,w['catalog']):
            raise ValueError('SQL validation failed')
        if sorted(labels[cid]['acceptable'])!=sorted(applicable(visible(w['events'],q),q,w['catalog'])):
            raise ValueError('Python validation failed')
    planned=[dict(case_id=cid,method=m,world=q['world']) for cid,q in cases.items()
             if not args.conditions or labels[cid]['condition'] in args.conditions for m in args.methods]
    random.Random(args.order_seed).shuffle(planned)
    for i,row in enumerate(planned):row['attempt_id']=i
    args.output.mkdir(parents=True,exist_ok=False)
    manifest=dict(kind='actual_local_model_'+dataset['split'],started_at=now(),complete=False,
        code_revision=git('rev-parse','HEAD'),source_sha256=code,working_tree_dirty=bool(git('status','--porcelain')),
        dataset_manifest=dataset,model_config=config,methods=args.methods,token_cap=args.token_cap,
        full_context_cap=15000,order_seed=args.order_seed,planned=planned,freeze=freeze,
        scope='Controlled fictional verified events; same model and planner; no human utility ratings or observed commercial outcomes.',
        runtime='llama.cpp a37cc46104eb50900d5ab4a9ba02a0abdac039db; CPU 4 threads; one slot; no prompt cache',
        model_sha256='3605803b982cb64aead44f6c1b2ae36e3acdb41d8e46c8a94c6533bc4c67e597',
        embedding_sha256='06507c7b42688469c4e7298b0a1e16deff06caf291cf0a5b278c308249c3e439',
        cost_methodology='Local CPU seconds and measured tokens; API spend zero, infrastructure price/energy unavailable. Cache origin receipts preserved.')
    mp=args.output/'manifest.json';mp.write_text(json.dumps(manifest,indent=2)+'\n')
    resources=LocalResources(args.embedding_cache,config['base_url'].removesuffix('/v1'))
    with (args.output/'attempts.jsonl').open('x') as stream:
        def emit(record):
            stream.write(canonical(record)+'\n');stream.flush();os.fsync(stream.fileno())
        for plan in planned:
            start=time.perf_counter()
            row=dict(plan,status='started',started_at=now())
            emit(row)
            q=cases[plan['case_id']];w=worlds[q['world']];label=labels[plan['case_id']]
            try:
                ev,retrieval=retrieve(w['events'],q,w['catalog'],plan['method'],resources,args.token_cap)
                msg=messages(q,w['catalog'],ev,plan['method'])
                truth=applicable(visible(w['events'],q),q,w['catalog'])
                supplied={e['id'] for e in ev}
                row.update(retrieval=retrieval,evidence_ids=sorted(supplied),messages=msg,prompt_sha256=hashlib.sha256(canonical(msg).encode()).hexdigest(),
                    support_available=any(all(group & supplied for group in groups) for groups in truth.values()),
                    condition=label['condition'],family=label['family'],positive=label['positive'])
                client.reserve(msg)
                emit(dict(row,status='model_call_started'))
                generation_start=time.perf_counter()
                response=client.complete(msg)
                row.update(response,generation_seconds=time.perf_counter()-generation_start)
                actual=response.get('usage',{}).get('prompt_tokens')
                if actual is not None and actual!=retrieval['prompt_tokens']:
                    raise ValueError('actual token usage differs from budget tokenizer')
                if plan['method']!='full_context' and actual is not None and actual>args.token_cap:
                    raise ValueError('input token cap exceeded')
                output=parse_json(response['raw_output'])
                row.update(output=output,score=score(output,w['events'],ev,q,w['catalog'],label['acceptable']),status='completed')
                if row['score']['dry_run']:
                    row['dry_run_execution']=execute(row['score']['dry_run'],visible(w['events'],q),q,w['catalog'])
            except Exception as exc:
                row.update(status='failed',error_type=type(exc).__name__)
                # Local-only endpoint; keep application validation messages, never arbitrary HTTP bodies.
                if isinstance(exc,ValueError):row['diagnostic']=str(exc)
            row.update(duration_seconds=time.perf_counter()-start,finished_at=now())
            emit(row)
            print(canonical({k:row[k] for k in ['attempt_id','case_id','method','status','duration_seconds']}),flush=True)
    manifest.update(complete=True,finished_at=now(),attempt_count=len(planned))
    mp.write_text(json.dumps(manifest,indent=2)+'\n')
    print(canonical({'complete':True,'attempts':len(planned),'path':str(args.output)}))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--model-config',type=Path,required=True)
    p.add_argument('--embedding-cache',type=Path,default=ROOT/'.cache/embeddings-v1.jsonl')
    p.add_argument('--methods',nargs='+',choices=METHODS,default=METHODS)
    p.add_argument('--conditions',nargs='+')
    p.add_argument('--token-cap',type=int,default=900)
    p.add_argument('--order-seed',type=int,default=20261022)
    p.add_argument('--freeze',type=Path)
    a=p.parse_args()
    if a.token_cap<=0 or len(a.methods)!=len(set(a.methods)):p.error('invalid cap or duplicate methods')
    run(a)


if __name__=='__main__':main()
