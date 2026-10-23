"""Execute the exact SQL policy reference on clean facts; not a model benchmark."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import time

from .contract import canonical, score, sql_oracle, visible
from .dryrun import execute


def run(data_path, output):
    manifest=json.loads((data_path/'manifest.json').read_text())
    for name,digest in manifest['files'].items():
        if hashlib.sha256((data_path/name).read_bytes()).hexdigest()!=digest:raise ValueError('data changed')
    data=json.loads((data_path/'inputs.json').read_text())
    labels={r['id']:r for r in json.loads((data_path/'labels.json').read_text())}
    worlds={w['id']:w for w in data['worlds']}
    output.mkdir(parents=True,exist_ok=False)
    rows=[]
    for case in data['queries']:
        q=case['query'];w=worlds[q['world']];start=time.perf_counter()
        witness=sql_oracle(w['events'],q,w['catalog'],witnesses=True)
        answer=dict(status='request_evidence',plays=[],missing=[])
        if witness:
            tid=sorted(witness)[0]
            answer=dict(status='recommend',plays=[dict(template=tid,evidence=[g[0] for g in witness[tid]])],missing=[])
        policy_seconds=time.perf_counter()-start
        ev=visible(w['events'],q)
        checked=score(answer,w['events'],ev,q,w['catalog'],labels[case['id']]['acceptable'])
        receipt=execute(checked['dry_run'],ev,q,w['catalog']) if checked['dry_run'] else None
        rows.append(dict(case_id=case['id'],world=q['world'],output=answer,score=checked,
            policy_seconds=policy_seconds,dry_run_execution=receipt))
    (output/'outputs.jsonl').write_text(''.join(canonical(r)+'\n' for r in rows))
    result=dict(kind='deterministic_SQL_policy_reference',model_calls=0,queries=len(rows),
        correct=sum(r['score']['decision_correct'] for r in rows),
        policy_seconds=sum(r['policy_seconds'] for r in rows),dataset_files=manifest['files'],
        created_at=datetime.now(timezone.utc).isoformat(),
        limitation='Exact policy evaluation on full verified facts. An executable oracle reference, not an end-to-end ingestion/memory baseline or strategic-utility test.')
    (output/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.data,a.output)
