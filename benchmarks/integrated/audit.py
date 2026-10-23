#!/usr/bin/env python3
"""Offline integrity audit: regenerate contexts and scores from real saved responses."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from benchmarks.integrated.common import *
from benchmarks.integrated.run import planned,usage_cost
from benchmarks.integrated.serialization import add_format
from benchmarks.recommendation.run import payload,decode,evaluate
from analysis.separate_context import context_metrics

def audit(data_root,packets,run,output):
    data=json.loads((data_root/'inputs.json').read_text());worlds={w['id']:w for w in data['worlds']}
    cases={c['id']:c for c in data['queries']}
    cm=json.loads((packets/'manifest.json').read_text());rm=json.loads((run/'manifest.json').read_text())
    assert cm['status']=='completed' and rm['status']=='completed'
    assert cm['data_sha256']==rm['data_sha256']==sha((data_root/'inputs.json').read_bytes())
    assert rm['packets_manifest_sha256']==sha((packets/'manifest.json').read_bytes())
    vectors={r['text']:r['vector'] for r in map(json.loads,(packets/'embedding-cache-snapshot.jsonl').read_text().splitlines())}
    assert cm['embedding_snapshot_sha256']==sha((packets/'embedding-cache-snapshot.jsonl').read_bytes())
    checked_packets=0;contexts=[]
    for cid,c in sorted(cases.items()):
        q=c['query'];w=worlds[q['world']]
        allowed=[e for e in visible(w['events'],q) if e['entity'] in ['seller',q['account']]]
        native=json.loads((packets/cid/'native.stdout.json').read_text())
        assert native['semantic_embedding_used'] and native['metadata']['vector_enabled']
        byid={e['id']:e for e in allowed};gbrain=[byid[r['id']] for r in native['rankings']]
        generic=rank_hybrid(allowed,q,w['catalog'],vectors)
        for p in json.loads((packets/cid/'packets.json').read_text()):
            selected=select(p['arm'],generic,gbrain,q,w['catalog'],p['budget_bytes'])
            ids=[e['id'] for e in selected]
            assert ids==p['evidence_ids'] and evidence_bytes(selected)==p['evidence_bytes']
            assert reader_messages(q,w['catalog'],selected)==p['messages']
            assert context_metrics(w['events'],q,w['catalog'],ids)==p['context']
            if p['arm'] not in ['none','full']:assert p['evidence_bytes']<=p['budget_bytes']
            checked_packets+=1
            contexts.append({k:p[k] for k in ['case_id','world','arm','budget_bytes','evidence_bytes','context']})
    assert planned(rm['config'],data,packets,rm['budget_bytes'])==rm['planned']
    ledger=[json.loads(s) for s in (run/'attempts.jsonl').read_text().splitlines()]
    issued=[r['id'] for r in ledger if r['status']=='issued']
    terminal=[r for r in ledger if r['status'] in ['completed','failed','interrupted']]
    assert len(set(issued))==len(issued)==len(rm['planned'])
    assert len({r['id'] for r in terminal})==len(terminal)==len(issued)
    by_attempt={r['id']:r for r in terminal};providers={p['provider']:p for p in rm['config']['providers']}
    rescored=0;response_ids=set()
    def unique_object(pairs):
        if len({k for k,v in pairs})!=len(pairs):raise ValueError('duplicate raw JSON keys')
        return dict(pairs)
    for p in rm['planned']:
        row=by_attempt[p['id']];folder=run/p['id'];provider=providers[p['provider']]
        assert row==json.loads((folder/'result.json').read_text())
        assert json.loads((folder/'request.json').read_text())==add_format(payload(provider,p['messages'],rm['config']['max_output_tokens']),p['provider'],p['messages'])
        if row['status']=='completed':
            obj=json.loads((folder/'response.json').read_text())
            assert obj['id'] not in response_ids
            response_ids.add(obj['id'])
            text,usage,finish,complete=decode(p['provider'],obj)
            assert complete and usage==row['usage'] and finish==row['finish_reason']
            assert usage_cost(p['provider'],usage,provider)==row['accounting']
            parsed=json.loads(text,object_pairs_hook=unique_object);explanation=parsed.pop('explanation');assert explanation==row['explanation']
            c=cases[p['case_id']];w=worlds[p['world']]
            evidence=[e for e in w['events'] if e['id'] in p['evidence_ids']]
            scored=evaluate(canonical(parsed),c,w,evidence)
            for k,v in scored.items():assert row[k]==v,(p['id'],k)
            rescored+=1
    for path,digest in rm['source_sha256'].items():
        assert sha((ROOT/path).read_bytes())==digest
        assert sha((run/'source-snapshot'/path).read_bytes())==digest
    output.mkdir(parents=True,exist_ok=False)
    (output/'contexts.jsonl').write_text(''.join(canonical(r)+'\n' for r in contexts))
    result={'passed':True,'cases':len(cases),'context_packets_rebuilt':checked_packets,'planned_reader_calls':len(issued),
        'raw_responses_rescored':rescored,'failures_retained':len(issued)-rescored,
        'source_hashes_verified':len(rm['source_sha256']),'fresh_api_calls':0,'fresh_native_search':False,
        'scope':'Saved real embedding vectors/native rankings; complete context and raw-response scoring reconstruction. No new model inference.',
        'manifest_sha256':sha((run/'manifest.json').read_bytes()),'ledger_sha256':sha((run/'attempts.jsonl').read_bytes())}
    (output/'audit.json').write_text(json.dumps(result,indent=2)+'\n');print(canonical(result))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['data','packets','run','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();audit(a.data,a.packets,a.run,a.output)
