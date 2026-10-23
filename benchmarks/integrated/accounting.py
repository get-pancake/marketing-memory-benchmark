#!/usr/bin/env python3
"""Account for unique saved provider responses, including unsuccessful attempts."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from benchmarks.integrated.common import ROOT,sha
from benchmarks.integrated.run import usage_cost

def compute(output):
    cfg=json.loads((ROOT/'benchmarks/integrated/providers.json').read_text())
    providers={p['provider']:p for p in cfg['providers']}
    entries=[];unknown=[];seen={};embedding=[]
    for scope in ['experiments/integrated','experiments/provider-access-2026-10-22']:
        for path in sorted((ROOT/scope).rglob('response.json')):
            obj=json.loads(path.read_text())
            if not isinstance(obj,dict) or not obj.get('usage'):continue
            model=obj.get('model','')
            if model.startswith('text-embedding-3-small'):
                tokens=obj['usage']['total_tokens']
                embedding.append({'path':str(path.relative_to(ROOT)),'tokens':tokens,'estimated_usd':tokens*.02/1e6})
                continue
            provider='openai' if model.startswith('gpt-6.1-sol') else 'anthropic' if model.startswith('claude-sonnet-5-5') else None
            if provider is None:raise ValueError('Unknown response model/pricing: '+model)
            key=obj['id'];accounting=usage_cost(provider,obj['usage'],providers[provider])
            if key in seen:
                if seen[key]!=accounting:raise ValueError('Same response ID has inconsistent accounting')
                continue
            seen[key]=accounting
            entries.append({'path':str(path.relative_to(ROOT)),'response_id':key,'provider':provider,
                'model':model,'response_sha256':sha(path.read_bytes()),**accounting})
        for path in sorted((ROOT/scope).rglob('result.json')):
            obj=json.loads(path.read_text())
            if obj.get('status') in ['failed','interrupted'] and not obj.get('usage'):
                unknown.append({'path':str(path.relative_to(ROOT)),'error_type':obj.get('error_type'),'http_status':obj.get('http_status'),
                    'note':'No usage receipt; no assertion of zero billing.'})
    grouped=defaultdict(lambda:{'responses':0,'estimated_usd':0,'input_tokens':0,'output_tokens':0})
    for row in entries:
        parts=Path(row['path']).parts;run=parts[2] if parts[1]=='integrated' else 'provider-access'
        group=grouped[run];group['responses']+=1;group['estimated_usd']+=float(row['estimated_usd'])
        group['input_tokens']+=row['total_input_tokens'];group['output_tokens']+=row['output_tokens']
    result={'scope':'Actual saved provider-usage list-price estimates, not reconciled invoices; excludes hardware, credits/taxes and unknown charges.',
        'known_unique_generation_responses':len(entries),'known_generation_usd':sum(float(r['estimated_usd']) for r in entries),
        'known_embedding_responses':len(embedding),'known_embedding_usd':sum(r['estimated_usd'] for r in embedding),
        'known_total_usd':sum(float(r['estimated_usd']) for r in entries)+sum(r['estimated_usd'] for r in embedding),
        'attempts_without_usage_receipt':unknown,'groups':dict(grouped),'responses':entries,'embedding_responses':embedding,
        'prices_sha256':sha((ROOT/'benchmarks/integrated/providers.json').read_bytes())}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['known_unique_generation_responses','known_total_usd','known_embedding_usd']}))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    compute(p.parse_args().output)
