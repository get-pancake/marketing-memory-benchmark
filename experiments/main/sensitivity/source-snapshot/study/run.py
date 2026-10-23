"""Execute a saved paired plan; actual model calls never fall back to mocks."""
import argparse
import fcntl
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import time
import urllib.error

from prototype.run import ModelClient, parse_json, git
from .contract import canonical, applicable, visible, sql_oracle, score
from .retrieval import METHODS, LocalResources, messages, retrieve, aliases, output_schema, materialize_output
from .dryrun import execute
from .ledger import atomic_json,recover

ROOT=Path(__file__).resolve().parents[1]
RESPONSE_FIELDS=['raw_output','request_json','usage','estimated_api_cost_usd','billed_cost_usd',
                 'local_compute_cost_included','response_model','response_id','system_fingerprint','finish_reason']


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()


def source_hashes():
    files=list((ROOT/'study').glob('*.py'))+[ROOT/'prototype/run.py',ROOT/'prototype/core.py',ROOT/'analysis/analyze_study.py']
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
    runtime=json.loads(args.runtime_manifest.read_text()) if args.runtime_manifest else {
        'model':'qwen3-4b-instruct-2507-q4_k_m',
        'model_sha256':'3605803b982cb64aead44f6c1b2ae36e3acdb41d8e46c8a94c6533bc4c67e597',
        'llama_cpp':'a37cc46104eb50900d5ab4a9ba02a0abdac039db',
        'threads':4,'context':16384,'parallel':1,'prompt_cache':False}
    if runtime['model']!=config['model']:raise ValueError('model runtime metadata is required and must match')
    freeze=json.loads(args.freeze.read_text()) if args.freeze else None
    reuse_identical=getattr(args,'reuse_identical',False)
    if dataset['split']=='test':
        if not freeze or freeze['source_sha256']!=code or freeze['dataset_files']!=dataset['files']:
            raise ValueError('test requires matching frozen code and data')
        if (freeze['model_config']!=config or freeze['methods']!=args.methods or
            freeze['token_cap']!=args.token_cap or freeze['order_seed']!=args.order_seed or
            freeze['runtime_manifest']!=runtime or freeze.get('reuse_identical',False)!=reuse_identical or args.conditions):
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
    if args.resume:
        if not args.output.is_dir():raise ValueError('resume directory is absent')
    else:args.output.mkdir(parents=True,exist_ok=False)
    run_lock=(args.output/'.run.lock').open('a')
    try:fcntl.flock(run_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:
        run_lock.close();raise ValueError('run is active; cannot resume')
    try:
        if not args.resume:
            for name,digest in code.items():
                payload=(ROOT/name).read_bytes()
                if hashlib.sha256(payload).hexdigest()!=digest:raise ValueError('source changed during initialization')
                target=args.output/'source-snapshot'/name
                target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload)
        manifest=dict(kind='actual_local_model_'+dataset['split'],started_at=now(),complete=False,
            code_revision=git('rev-parse','HEAD'),source_sha256=code,working_tree_dirty=bool(git('status','--porcelain')),
            dataset_manifest=dataset,model_config=config,methods=args.methods,token_cap=args.token_cap,
            full_context_cap=15000,order_seed=args.order_seed,planned=planned,freeze=freeze,
            scope='Controlled fictional verified events; same model and planner; no human utility ratings or observed commercial outcomes.',
            runtime=runtime,
            reuse_identical=reuse_identical,
            embedding_cache_path=str(args.embedding_cache),
            model_sha256=runtime['model_sha256'],
            embedding_sha256='06507c7b42688469c4e7298b0a1e16deff06caf291cf0a5b278c308249c3e439',
            cost_methodology='Local CPU seconds and measured tokens; API spend zero, infrastructure price/energy unavailable. Identical requests, when enabled, reuse actual returned outputs including errors; logical token/time charges use the origin call, physical calls/time are separate. Embedding cache origins preserved.')
        mp=args.output/'manifest.json';terminal=set();pending=[]
        if args.resume:
            previous=json.loads(mp.read_text())
            if previous['complete']:raise ValueError('run is already complete; no inference repeated')
            for key in ['source_sha256','dataset_manifest','model_config','runtime','methods','token_cap','order_seed','planned','freeze','reuse_identical']:
                if previous[key]!=manifest[key]:raise ValueError('resume differs from saved '+key)
            for name,digest in code.items():
                if sha(args.output/'source-snapshot'/name)!=digest:raise ValueError('snapshot changed')
            terminal,pending,recovery=recover(args.output/'attempts.jsonl',planned)
            manifest=previous
            manifest.setdefault('resumptions',[]).append(dict(at=now(),code_revision=git('rev-parse','HEAD'),recoveries=recovery))
        atomic_json(mp,manifest)
        responses={}
        if args.resume and reuse_identical:
            for line in (args.output/'attempts.jsonl').read_text().splitlines():
                r=json.loads(line)
                if r['status'] in ['completed','failed'] and 'request_json' in r and 'raw_output' in r:
                    responses.setdefault(r['request_json'],({k:r[k] for k in RESPONSE_FIELDS if k in r},
                        r['generation_seconds'],r.get('reused_from_attempt_id',r['attempt_id'])))
        resources=LocalResources(args.embedding_cache,config['base_url'].removesuffix('/v1'))
        with (args.output/'attempts.jsonl').open('a' if args.resume else 'x') as stream:
            def emit(record):
                stream.write(canonical(record)+'\n');stream.flush();os.fsync(stream.fileno())
            for interrupted in pending:
                emit(dict(interrupted,status='failed',error_type='Interrupted',
                    diagnostic='Issued attempt has no saved terminal result; not retried. Usage and inference duration may be unknown.',
                    duration_seconds=None,finished_at=now()))
                terminal.add(interrupted['attempt_id'])
            for plan in planned:
                if plan['attempt_id'] in terminal:continue
                start=time.perf_counter()
                row=dict(plan,status='started',started_at=now())
                emit(row)
                q=cases[plan['case_id']];w=worlds[q['world']];label=labels[plan['case_id']]
                transport_failed=False
                try:
                    ev,retrieval=retrieve(w['events'],q,w['catalog'],plan['method'],resources,args.token_cap)
                    msg=messages(q,w['catalog'],ev,plan['method'])
                    truth=applicable(visible(w['events'],q),q,w['catalog'])
                    supplied={e['id'] for e in ev}
                    row.update(retrieval=retrieval,evidence_ids=sorted(supplied),messages=msg,prompt_sha256=hashlib.sha256(canonical(msg).encode()).hexdigest(),
                        source_aliases=aliases(ev),response_format=output_schema(w['catalog'],ev),
                        support_available=any(all(group & supplied for group in groups) for groups in truth.values()),
                        condition=label['condition'],family=label['family'],positive=label['positive'])
                    client.reserve(msg)
                    request_json=client.request_json(msg,row['response_format']) if reuse_identical else None
                    if request_json is not None:
                        row.update(request_json=request_json,request_sha256=hashlib.sha256(request_json.encode()).hexdigest())
                    cached=responses.get(request_json) if reuse_identical else None
                    row['model_request_reused']=cached is not None
                    if cached is not None:
                        response,seconds,origin=cached
                        row.update(generation_seconds=seconds,physical_generation_seconds=0,reused_from_attempt_id=origin)
                        emit(dict(row,status='model_call_reused'))
                    else:
                        emit(dict(row,status='model_call_started'))
                        generation_start=time.perf_counter()
                        try:response=client.complete(msg,response_format=row['response_format'])
                        finally:
                            row['generation_seconds']=time.perf_counter()-generation_start
                            row['physical_generation_seconds']=row['generation_seconds']
                        if reuse_identical:
                            if response['request_json']!=request_json:raise ValueError('request serialization changed')
                            # Preserve returned failures/truncation too; never cache only correct answers.
                            responses[request_json]=(dict(response),row['generation_seconds'],plan['attempt_id'])
                    row.update(response)
                    actual=response.get('usage',{}).get('prompt_tokens')
                    if actual is not None and actual!=retrieval['prompt_tokens']:
                        raise ValueError('actual token usage differs from budget tokenizer')
                    if plan['method']!='full_context' and actual is not None and actual>args.token_cap:
                        raise ValueError('input token cap exceeded')
                    unbound=parse_json(response['raw_output'])
                    row['unbound_output']=unbound
                    output,bindings=materialize_output(unbound,ev,w['catalog'])
                    row.update(output=output,slot_bindings=bindings,
                        score=score(output,w['events'],ev,q,w['catalog'],label['acceptable'],bindings),status='completed')
                    if row['score']['dry_run']:
                        row['dry_run_execution']=execute(row['score']['dry_run'],visible(w['events'],q),q,w['catalog'])
                except Exception as exc:
                    transport_failed=isinstance(exc,(urllib.error.URLError,TimeoutError,ConnectionError))
                    row.update(status='failed',error_type=type(exc).__name__)
                    # Local-only endpoint; keep application validation messages, never arbitrary HTTP bodies.
                    if isinstance(exc,ValueError):row['diagnostic']=str(exc)
                row.update(duration_seconds=time.perf_counter()-start,finished_at=now())
                emit(row)
                terminal.add(plan['attempt_id'])
                atomic_json(args.output/'progress.json',dict(updated_at=now(),terminal_attempts=len(terminal),planned=len(planned)))
                print(canonical({k:row[k] for k in ['attempt_id','case_id','method','status','duration_seconds']}),flush=True)
                if transport_failed:raise RuntimeError('Local transport failed; preserve run and resume unstarted attempts after repair')
        manifest.update(complete=True,finished_at=now(),attempt_count=len(planned))
        atomic_json(mp,manifest)
        print(canonical({'complete':True,'attempts':len(planned),'path':str(args.output)}))
    finally:run_lock.close()


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
    p.add_argument('--runtime-manifest',type=Path)
    p.add_argument('--resume',action='store_true',help='Close interrupted attempts as failed; continue unstarted work without retrying completed calls')
    p.add_argument('--reuse-identical',action='store_true',help='One actual returned response per identical serialized request; record origin and charge its tokens/time to every logical comparison')
    a=p.parse_args()
    if a.token_cap<=0 or len(a.methods)!=len(set(a.methods)):p.error('invalid cap or duplicate methods')
    run(a)


if __name__=='__main__':main()
