"""Durable accounting and conservative recovery for interrupted experiments."""
import hashlib
import json
import os
from pathlib import Path


def atomic_json(path,value):
    path=Path(path);temporary=path.with_name(path.name+'.tmp')
    with temporary.open('w') as f:
        json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    temporary.replace(path)


def recover(path,planned):
    """Keep complete records; preserve a torn final append before repairing it.

    An issued request without a terminal record is not retried or invented.
    The caller closes it as interrupted and proceeds only to unstarted work.
    Must be called while holding the exclusive run lock.
    """
    path=Path(path);payload=path.read_bytes() if path.exists() else b''
    lines=payload.splitlines(keepends=True);records=[];recoveries=[];offset=0
    for i,line in enumerate(lines):
        try:record=json.loads(line)
        except (json.JSONDecodeError,UnicodeDecodeError):
            if i!=len(lines)-1 or line.endswith(b'\n'):raise ValueError('corrupt complete ledger record')
            digest=hashlib.sha256(line).hexdigest();archive=path.parent/'recovery'/('tail-'+digest+'.bin')
            archive.parent.mkdir(exist_ok=True);archive.write_bytes(line)
            temporary=path.with_name(path.name+'.recovered')
            with temporary.open('wb') as f:f.write(payload[:offset]);f.flush();os.fsync(f.fileno())
            temporary.replace(path)
            recoveries.append(dict(kind='torn_final_append',path=str(archive.relative_to(path.parent)),sha256=digest,bytes=len(line)))
            break
        records.append(record);offset+=len(line)
    else:
        if payload and not payload.endswith(b'\n'):
            with path.open('ab') as f:f.write(b'\n');f.flush();os.fsync(f.fileno())
            recoveries.append(dict(kind='completed_newline_after_valid_JSON'))
    plans={p['attempt_id']:p for p in planned}
    if len(plans)!=len(planned):raise ValueError('duplicate planned attempt')
    latest={};terminal=set()
    for record in records:
        aid=record.get('attempt_id')
        if aid not in plans or any(record.get(k)!=v for k,v in plans[aid].items()):
            raise ValueError('ledger identity differs from plan')
        if aid in terminal:raise ValueError('record after terminal attempt')
        if record['status'] in ['completed','failed']:terminal.add(aid)
        elif record['status'] not in ['started','model_call_started','model_call_reused']:raise ValueError('unknown ledger state')
        latest[aid]=record
    pending=[r for aid,r in latest.items() if aid not in terminal]
    return terminal,pending,recoveries
