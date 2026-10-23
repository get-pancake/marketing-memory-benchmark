#!/usr/bin/env python3
"""Check complete run provenance, input boundaries and actual-response reuse."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from study.contract import canonical,visible
from study.retrieval import aliases, messages, output_schema
from prototype.run import ModelClient


def audit(run,data,output):
    manifest=json.loads((run/'manifest.json').read_text())
    if not manifest['complete']:raise ValueError('run is incomplete')
    for name,digest in manifest['source_sha256'].items():
        if hashlib.sha256((run/'source-snapshot'/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('source snapshot mismatch')
    for name in ['study/retrieval.py', 'prototype/run.py']:
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=manifest['source_sha256'].get(name):
            raise ValueError('Prompt/request reconstruction requires the matching archived producer: '+name)
    client=ModelClient(manifest['model_config'])
    if not client.local:raise ValueError('This audit expects the recorded local model configuration')
    for name,digest in manifest['dataset_manifest']['files'].items():
        if hashlib.sha256((data/name).read_bytes()).hexdigest()!=digest:raise ValueError('data mismatch')
    inputs=json.loads((data/'inputs.json').read_text())
    worlds={w['id']:w for w in inputs['worlds']};queries={c['id']:c['query'] for c in inputs['queries']}
    planned={p['attempt_id']:p for p in manifest['planned']}
    rows=[json.loads(line) for line in (run/'attempts.jsonl').read_text().splitlines()]
    calls={r['attempt_id'] for r in rows if r['status']=='model_call_started'}
    if len(calls)!=sum(r['status']=='model_call_started' for r in rows):
        raise ValueError('duplicate physical-call start')
    reconstructed_inputs=0;reconstructed_requests=0
    terminal={}
    for r in rows:
        if r['attempt_id'] not in planned:raise ValueError('unplanned attempt')
        if r['status'] not in ['completed','failed']:continue
        aid=r['attempt_id']
        if aid in terminal:raise ValueError('duplicate terminal')
        if any(r.get(k)!=v for k,v in planned[aid].items()):raise ValueError('attempt identity mismatch')
        terminal[aid]=r
        if 'messages' not in r:continue
        if hashlib.sha256(canonical(r['messages']).encode()).hexdigest()!=r['prompt_sha256']:
            raise ValueError('prompt hash mismatch')
        q=queries[r['case_id']];w=worlds[r['world']]
        allowed=visible(w['events'],q,retain_superseded=r['method']=='typed_history')
        allowed=[e for e in allowed if e['entity'] in ['seller',q['account']]]
        if not set(r['evidence_ids'])<={e['id'] for e in allowed}:raise ValueError('future/scope/source boundary violated')
        selected=[e for e in allowed if e['id'] in r['evidence_ids']]
        expected_messages=messages(q,w['catalog'],selected,r['method'])
        expected_schema=output_schema(w['catalog'],selected)
        if r['messages']!=expected_messages:
            raise ValueError('prompt content differs from source facts, catalog or shared instructions')
        if r['source_aliases']!=aliases(selected) or r['response_format']!=expected_schema:
            raise ValueError('source aliases or output grammar differ from the public input')
        reconstructed_inputs+=1
        payload=json.loads(r['messages'][1]['content'])
        if payload['query']!={k:v for k,v in q.items() if k!='world'}:raise ValueError('query differs')
        if {t['id'] for t in payload['catalog']}!={t['id'] for t in w['catalog']}:raise ValueError('catalog alternatives removed')
        if 'request_json' in r:
            if r['request_json']!=client.request_json(expected_messages,expected_schema):
                raise ValueError('serialized request differs from recorded decoding settings or schema order')
            reconstructed_requests+=1
            request=json.loads(r['request_json'])
            if request['messages']!=r['messages'] or request['response_format']!=r['response_format']:
                raise ValueError('saved request differs from trace')
            if request['model']!=manifest['model_config']['model']:raise ValueError('model request differs')
            if r.get('request_sha256') and hashlib.sha256(r['request_json'].encode()).hexdigest()!=r['request_sha256']:
                raise ValueError('request hash mismatch')
        if 'raw_output' in r:
            if r['response_model']!=manifest['model_config']['model']:raise ValueError('response model differs')
            tokens=r['usage']['prompt_tokens']
            if tokens!=r['retrieval']['prompt_tokens']:raise ValueError('tokenizer mismatch')
            if r['method']!='full_context' and tokens>manifest['token_cap']:raise ValueError('token cap exceeded')
            if r.get('model_request_reused'):
                origin=terminal[r['reused_from_attempt_id']]
                if origin.get('model_request_reused') or origin['attempt_id'] not in calls:
                    raise ValueError('cache origin was not an actual call')
                for field in ['request_json','raw_output','usage','response_id','generation_seconds']:
                    if r[field]!=origin[field]:raise ValueError('reused output differs from origin')
                if r['physical_generation_seconds']!=0:raise ValueError('reused call charged as physical')
            elif aid not in calls:raise ValueError('returned output has no issued call')
    if set(terminal)!=set(planned):raise ValueError('planned attempts missing')
    result=dict(passed=True,planned=len(planned),terminal=len(terminal),physical_calls=len(calls),
        reused_requests=sum(bool(r.get('model_request_reused')) for r in terminal.values()),
        statuses=dict(Counter(r['status'] for r in terminal.values())),
        source_snapshot_files=len(manifest['source_sha256']),
        reconstructed_inputs=reconstructed_inputs,reconstructed_requests=reconstructed_requests,
        ledger_sha256=hashlib.sha256((run/'attempts.jsonl').read_bytes()).hexdigest(),
        limits='Artifact consistency and explicit input-boundary checks, not independent human validation or a formal security proof.')
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',type=Path,required=True);p.add_argument('--data',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();audit(a.run,a.data,a.output)
