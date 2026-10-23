#!/usr/bin/env python3
"""Disclosed post-hoc sensitivity to one ambiguous upstream development label."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from benchmarks.integrated.common import sha

def compute(base,chunks,output):
    a=[json.loads(s) for s in base.read_text().splitlines()]
    b=[json.loads(s) for s in chunks.read_text().splitlines()]
    for r in b:r['correct']=int(r['answer_correct'])
    rows=a+b;groups={}
    for provider,arm in sorted({(r['provider'],r['arm']) for r in rows}):
        rs=[r for r in rows if r['provider']==provider and r['arm']==arm]
        kept=[r for r in rs if r['case_id']!='dev-op-2']
        groups[provider+'/'+arm]={'all_correct':sum(r['correct'] for r in rs),'all_cases':len(rs),
            'sensitivity_correct':sum(r['correct'] for r in kept),'sensitivity_cases':len(kept)}
    result={'kind':'post-hoc descriptive sensitivity; original scoring unchanged',
        'excluded_case':'dev-op-2','reason':'Upstream requires ambiguity, while nearby QBR prose motivates a plausible but non-unique account inference. This case drives some one-answer advantages.',
        'groups':groups,'input_sha256':{'base':sha(base.read_bytes()),'chunks':sha(chunks.read_bytes())}}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(groups))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['base','chunks','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();compute(a.base,a.chunks,a.output)
