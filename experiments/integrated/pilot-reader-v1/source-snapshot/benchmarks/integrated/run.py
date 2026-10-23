#!/usr/bin/env python3
"""Actual crossed provider/context benchmark with immutable attempt accounting.

Requires user-authorized API credentials in process environment. A numerical
operational cap is chosen by the operator, not represented as user-specified.
No automatic retries or replacement responses; API failures stay in denominators.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
from decimal import Decimal
import fcntl
import json
import os
from pathlib import Path
import random
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from benchmarks.integrated.common import *
from benchmarks.recommendation.run import decode,evaluate,payload

ENDPOINTS={'openai':'https://api.openai.com/v1/responses','anthropic':'https://api.anthropic.com/v1/messages'}
KEYS={'openai':'RESEARCH_OPENAI_API_KEY','anthropic':'RESEARCH_ANTHROPIC_API_KEY'}
def now():return datetime.now(timezone.utc).isoformat()

def usage_cost(provider,usage,config):
    """Handle distinct provider cache accounting. Returns list-price estimate."""
    inp=usage['input_tokens'];out=usage['output_tokens']
    if provider=='openai':
        detail=usage.get('input_tokens_details',{})
        read=detail.get('cached_tokens',0);write=detail.get('cache_write_tokens',0)
        regular=inp-read-write;total=inp;write1h=0
    else:
        read=usage.get('cache_read_input_tokens',0);write=usage.get('cache_creation_input_tokens',0)
        write1h=usage.get('cache_creation',{}).get('ephemeral_1h_input_tokens',0)
        regular=inp;total=inp+read+write
    if any(not isinstance(x,int) or x<0 for x in [regular,read,write,out,total,write1h]) or write1h>write:
        raise ValueError('unsupported/invalid usage accounting')
    if write1h and config['cache_write_extended_usd_per_million'] is None:
        raise ValueError('unexpected extended-cache writes: price not verified')
    extended_cost=Decimal(write1h)*Decimal(str(config['cache_write_extended_usd_per_million'])) if write1h else Decimal(0)
    estimated=(Decimal(regular)*Decimal(str(config['input_usd_per_million']))+
        Decimal(read)*Decimal(str(config['cache_read_usd_per_million']))+
        Decimal(write-write1h)*Decimal(str(config['cache_write_usd_per_million']))+extended_cost+
        Decimal(out)*Decimal(str(config['output_usd_per_million'])))/Decimal(1000000)
    return {'estimated_usd':str(estimated),'total_input_tokens':total,'output_tokens':out,
            'regular_input_tokens':regular,'cache_read_tokens':read,'cache_write_tokens':write}

def reserve(messages,config,max_output):
    upper=sum(len(m['content'].encode()) for m in messages)+4096
    rate=Decimal(str(config['reservation_input_usd_per_million']))
    amount=(upper*rate+max_output*Decimal(str(config['output_usd_per_million'])))/Decimal(1000000)
    return upper,amount

def planned(config,data,packets_root,cap):
    result=[]
    for case in sorted(data['queries'],key=lambda c:c['id']):
        path=packets_root/case['id']/'packets.json'
        for packet in json.loads(path.read_text()):
            if packet['budget_bytes']!=cap:continue
            for provider in config['providers']:
                upper,amount=reserve(packet['messages'],provider,config['max_output_tokens'])
                result.append({'id':case['id']+'-'+provider['provider']+'-'+packet['arm'],
                    'case_id':case['id'],'world':packet['world'],'arm':packet['arm'],'provider':provider['provider'],
                    'messages':packet['messages'],'evidence_ids':packet['evidence_ids'],
                    'context':packet['context'],'evidence_bytes':packet['evidence_bytes'],
                    'input_upper_bound':upper,'reserved_usd':str(amount),'packet_file_sha256':sha(path.read_bytes())})
    random.Random(config['order_seed']).shuffle(result)
    if len({r['id'] for r in result})!=len(result):raise ValueError('duplicate planned request')
    return result

def append(path,row):
    with path.open('a') as f:f.write(canonical(row)+'\n');f.flush();os.fsync(f.fileno())

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['config','data','packets','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--cap-bytes',type=int,default=2048)
    p.add_argument('--execute',action='store_true');p.add_argument('--resume',action='store_true')
    p.add_argument('--operational-cap-usd',type=Decimal)
    p.add_argument('--workers',type=int,default=4)
    a=p.parse_args();cfg=json.loads(a.config.read_text());data=json.loads((a.data/'inputs.json').read_text())
    plans=planned(cfg,data,a.packets,a.cap_bytes)
    hashes={str(f.resolve().relative_to(ROOT)):sha(f.read_bytes()) for f in [Path(__file__),Path(__file__).with_name('common.py'),ROOT/'benchmarks/recommendation/run.py',ROOT/'study/contract.py',ROOT/'study/retrieval.py']}
    manifest={'created_at':now(),'config':cfg,'data_sha256':sha((a.data/'inputs.json').read_bytes()),'source_sha256':hashes,
        'packets_manifest_sha256':sha((a.packets/'manifest.json').read_bytes()),'budget_bytes':a.cap_bytes,'planned':plans,
        'reservation_total_usd':str(sum((Decimal(r['reserved_usd']) for r in plans),Decimal(0))),
        'status':'planned','executed':False,'user_supplied_numerical_limit':None,
        'authorization':'User explicitly authorized provider API benchmark execution; numerical guard is researcher-selected.',
        'billed_cost_verified':False}
    if not a.execute:
        a.output.mkdir(parents=True,exist_ok=False);(a.output/'plan.json').write_text(json.dumps(manifest,indent=2)+'\n')
        print(canonical({'requests':len(plans),'reservation_total_usd':manifest['reservation_total_usd'],'executed':False}));return
    if a.operational_cap_usd is None or not a.operational_cap_usd.is_finite() or a.operational_cap_usd<=0:raise ValueError('positive operational cap required')
    if Decimal(manifest['reservation_total_usd'])>a.operational_cap_usd:raise ValueError('entire planned experiment exceeds operational cap; no requests issued')
    if len(plans)>cfg['max_requests'] or any(r['input_upper_bound']>cfg['max_input_upper_bound'] for r in plans):raise ValueError('request/input envelope exceeded')
    for provider in cfg['providers']:
        if not os.environ.get(KEYS[provider['provider']]):raise ValueError('missing provider credential')
        if not provider['model'] or not provider['price_source'] or not provider['price_checked_at']:raise ValueError('unverified model/pricing')
    if not a.resume:a.output.mkdir(parents=True,exist_ok=False)
    lock=(a.output/'.run.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    ledger=a.output/'attempts.jsonl';old=[]
    if a.resume:
        previous=json.loads((a.output/'manifest.json').read_text())
        for key in ['config','data_sha256','source_sha256','packets_manifest_sha256','budget_bytes','planned']:
            if previous[key]!=manifest[key]:raise ValueError('resume would change frozen experiment: '+key)
        if ledger.exists():old=[json.loads(line) for line in ledger.read_text().splitlines()]
    started={r['id'] for r in old if r['status']=='issued'}
    done={r['id'] for r in old if r['status'] in ['completed','failed','interrupted']}
    for identity in sorted(started-done):append(ledger,{'id':identity,'status':'interrupted','at':now(),'note':'Never reissued; full reservation retained.'})
    manifest.update(status='running',executed=True,operational_cap_usd=str(a.operational_cap_usd))
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    snapshot=a.output/'source-snapshot'
    if not a.resume:
        for path,digest in hashes.items():
            target=snapshot/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/path).read_bytes())
    worlds={w['id']:w for w in data['worlds']};cases={c['id']:c for c in data['queries']};providers={p['provider']:p for p in cfg['providers']}
    def call(plan):
        provider=providers[plan['provider']];folder=a.output/plan['id'];folder.mkdir(exist_ok=False)
        body=payload(provider,plan['messages'],cfg['max_output_tokens'])
        (folder/'request.json').write_text(canonical(body)+'\n')
        headers={'Content-Type':'application/json'}
        if plan['provider']=='openai':headers['Authorization']='Bearer '+os.environ[KEYS['openai']]
        else:headers.update({'x-api-key':os.environ[KEYS['anthropic']],'anthropic-version':'2023-06-01'})
        row={k:plan[k] for k in ['id','case_id','world','arm','provider','context','evidence_bytes']}
        row.update(status='failed',started_at=now());start=time.perf_counter()
        try:
            req=urllib.request.Request(ENDPOINTS[plan['provider']],data=canonical(body).encode(),headers=headers)
            with urllib.request.urlopen(req,timeout=180) as response:raw=response.read(16*1024*1024)
            (folder/'response.json').write_bytes(raw);obj=json.loads(raw)
            text,usage,finish,complete=decode(plan['provider'],obj)
            row.update(response_model=obj.get('model'),response_id=obj.get('id'),usage=usage,finish_reason=finish,
                       accounting=usage_cost(plan['provider'],usage,provider))
            if row['accounting']['total_input_tokens']>plan['input_upper_bound'] or row['accounting']['output_tokens']>cfg['max_output_tokens']:
                raise ValueError('usage exceeds conservative reservation envelope')
            if not complete:raise ValueError('incomplete output')
            parsed=json.loads(text)
            if not isinstance(parsed,dict) or set(parsed)!={'support','status','template','missing','explanation'} or not isinstance(parsed['explanation'],str):raise ValueError('output schema mismatch')
            explanation=parsed.pop('explanation')
            case=cases[plan['case_id']];world=worlds[case['query']['world']]
            evidence=[e for e in world['events'] if e['id'] in plan['evidence_ids']]
            row.update(evaluate(canonical(parsed),case,world,evidence),explanation=explanation,status='completed')
        except urllib.error.HTTPError as error:
            # Error responses cannot contain our authorization header. Still do
            # not retain arbitrary error text; only safe structured codes.
            row.update(error_type='HTTPError',http_status=error.code)
        except Exception as error:row.update(error_type=type(error).__name__)
        row.update(finished_at=now(),seconds=time.perf_counter()-start)
        (folder/'result.json').write_text(json.dumps(row,indent=2)+'\n')
        return row
    pending=[r for r in plans if r['id'] not in started]
    # Bounded waves preserve issued status before any network request. A failed
    # provider does not get extra opportunities or silently changed settings.
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        for offset in range(0,len(pending),a.workers):
            wave=pending[offset:offset+a.workers]
            for plan in wave:append(ledger,{'id':plan['id'],'status':'issued','at':now(),'reserved_usd':plan['reserved_usd']})
            futures=[pool.submit(call,plan) for plan in wave]
            stop=False
            for future in as_completed(futures):
                row=future.result();append(ledger,row)
                print(canonical({'id':row['id'],'status':row['status'],'seconds':round(row['seconds'],2),'cost':row.get('accounting',{}).get('estimated_usd')}),flush=True)
                stop|=row.get('http_status') in [401,403,429] or (row.get('accounting',{}).get('total_input_tokens',0)>next(r['input_upper_bound'] for r in wave if r['id']==row['id']))
            if stop:
                manifest['status']='provider_or_usage_stop';break
        else:manifest['status']='completed'
    terminals=[json.loads(s) for s in ledger.read_text().splitlines() if json.loads(s)['status'] in ['completed','failed','interrupted']]
    manifest.update(finished_at=now(),attempted=len(terminals),successful=sum(r['status']=='completed' for r in terminals),
        estimated_usage_cost_usd=str(sum((Decimal(r.get('accounting',{}).get('estimated_usd','0')) for r in terminals),Decimal(0))))
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

if __name__=='__main__':main()
