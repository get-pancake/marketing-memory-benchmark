#!/usr/bin/env python3
"""Fixed-context Claude/GPT pilot: offline planning; explicit capped API execution.

No subscription-token reuse, implicit model choice, answer repair, automatic retry
or unavailable-provider simulation. API requests require separately configured keys.
"""
import argparse
import fcntl
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from study.contract import canonical, visible, slot_name, score, applicable
from study.retrieval import messages, materialize_output

ENDPOINTS={'openai':'https://api.openai.com/v1/responses',
           'anthropic':'https://api.anthropic.com/v1/messages'}
KEYS={'openai':'RESEARCH_OPENAI_API_KEY','anthropic':'RESEARCH_ANTHROPIC_API_KEY'}
def api_key(provider):
    # Managed cloud reserves OPENAI_* target names; standalone environments may
    # already provide the conventional names. Never print either value.
    conventional={'openai':'OPENAI_API_KEY','anthropic':'ANTHROPIC_API_KEY'}
    return os.environ.get(KEYS[provider]) or os.environ.get(conventional[provider])
COMMON='''Use only the supplied company evidence and action catalog. Proposals and feedback do not change approved policy. Current conflicting values block the affected requirement. Recommend one action only if its objective, budget, all its own requirements and equalities are satisfied; otherwise request evidence. Never assume a missing fact. Return only JSON with support, status, template, missing. The support object maps EVERY catalog relation identifier (entity.relation:authority, without =value) to one supplied source label or null. status is recommend or request_evidence; template is its catalog ID or null; missing is a string array. Bind sources to their exact entity, relation and authority. Cite only supplied evidence. These are research actions, not revenue predictions.'''
SCAFFOLD=''' Check each candidate separately against the objective, resource allowance, prerequisites and equalities. A missing fact needed only by one candidate must not block a different eligible candidate. Check the chosen candidate's source bindings before returning. Make no change to policy.'''

def now():return datetime.now(timezone.utc).isoformat()
def sha(x):return hashlib.sha256(x).hexdigest()

def case_messages(case,world,method):
    q=case['query'];catalog=world['catalog']
    # Public catalog-conditioned fixed context is supplied equally to both
    # methods. Include all authorities and conflicting values for its slots.
    # No gold answer, future record or source label from outcomes enters here.
    keys={(q['account'] if r['entity']=='$account' else r['entity'],r['key'])
          for t in catalog for r in t['requirements']}
    evidence=[e for e in visible(world['events'],q) if (e['entity'],e['key']) in keys]
    msg=messages(q,catalog,evidence,'prompt_hybrid')
    msg[0]['content']=COMMON+(SCAFFOLD if method=='candidate_checks' else '')
    return msg,evidence

def input_bound(msg):
    # Conservative UTF-8-byte bound plus fixed provider framing allowance;
    # not a claim to implement either provider's exact tokenizer. Exceeding
    # the bound in observed usage is a protocol/cost-control failure.
    return sum(len(m['content'].encode()) for m in msg)+1024

def cost(config,input_tokens,output_tokens):
    return (Decimal(str(config['input_usd_per_million']))*input_tokens+
            Decimal(str(config['output_usd_per_million']))*output_tokens)/Decimal(1000000)

def prepare(config,data):
    worlds={w['id']:w for w in data['worlds']}
    cases=sorted(data['queries'],key=lambda x:x['id'])[:16]
    if len(cases)!=16:raise ValueError('pilot requires exactly 16 development cases')
    planned=[]
    providers=config['providers']
    if {p['provider'] for p in providers}!={'openai','anthropic'} or len(providers)!=2:
        raise ValueError('configure each required provider exactly once')
    for provider in providers:
        for case in cases:
            for method in ['direct','candidate_checks']:
                msg,evidence=case_messages(case,worlds[case['query']['world']],method)
                upper=input_bound(msg)
                planned.append(dict(id=provider['provider']+'-'+case['id']+'-'+method,
                    provider=provider['provider'],model=provider['model'],case_id=case['id'],method=method,
                    context_sha256=sha(msg[1]['content'].encode()),messages=msg,
                    evidence_ids=[e['id'] for e in evidence],input_token_upper_bound=upper,
                    within_input_bound=upper<=config['max_input_tokens'],
                    reserved_usd=(str(cost(provider,upper,config['max_output_tokens']))
                      if all(provider.get(k) is not None for k in ['input_usd_per_million','output_usd_per_million']) else None)))
    for cid in {p['case_id'] for p in planned}:
        if len({p['context_sha256'] for p in planned if p['case_id']==cid})!=1:
            raise ValueError('fixed-context equality violated')
    order={case['id']:i for i,case in enumerate(cases)}
    provider_order={'openai':0,'anthropic':1};method_order={'direct':0,'candidate_checks':1}
    planned.sort(key=lambda r:(order[r['case_id']],
        (2*provider_order[r['provider']]+method_order[r['method']]-order[r['case_id']])%4))
    return planned

def payload(provider,msg,max_output):
    if provider['provider']=='openai':
        permitted={'reasoning','temperature','top_p'}
        obj=dict(model=provider['model'],input=msg,max_output_tokens=max_output,store=False)
    else:
        permitted={'temperature','top_p','thinking'}
        obj=dict(model=provider['model'],system=msg[0]['content'],messages=[msg[1]],max_tokens=max_output)
    if set(provider.get('request_options',{}))-permitted:
        raise ValueError('unsupported request option')
    obj.update(provider.get('request_options',{}))
    return obj

def decode(provider,response):
    if provider=='openai':
        text=''.join(c.get('text','') for m in response.get('output',[])
                     if m.get('type')=='message' for c in m.get('content',[]) if c.get('type')=='output_text')
        usage=response.get('usage',{});finish=response.get('status')
        complete=finish=='completed'
    else:
        text=''.join(c.get('text','') for c in response.get('content',[]) if c.get('type')=='text')
        usage=response.get('usage',{});finish=response.get('stop_reason');complete=finish=='end_turn'
    return text,usage,finish,complete

def evaluate(text,case,world,evidence):
    raw=json.loads(text)
    output,bindings=materialize_output(raw,evidence,world['catalog'])
    truth=applicable(visible(world['events'],case['query']),case['query'],world['catalog'])
    scored=score(output,world['events'],evidence,case['query'],world['catalog'],sorted(truth),bindings)
    # Validation uses the supplied context, NEVER hidden/full-world labels.
    # The fixed-context boundary already supplies current records. Remove only
    # out-of-packet historical replacement pointers for this local closed view;
    # never import the replaced facts or consult the hidden world as validation.
    local_events=[dict(e,supersedes=[]) for e in evidence]
    local_truth=applicable(local_events,case['query'],world['catalog'])
    checked=score(output,local_events,local_events,case['query'],world['catalog'],sorted(local_truth),bindings)
    rejected=output['status']=='recommend' and not checked['supported_recommendation']
    validated=({'status':'request_evidence','plays':[], 'missing':['proposal_failed_explicit_checks']}
               if rejected else output)
    validated_score=score(validated,world['events'],evidence,case['query'],world['catalog'],sorted(truth),
                          None if rejected else bindings)
    return dict(raw_output=raw,materialized=output,raw_score=scored,validator_rejected=rejected,
                validated_output=validated,validated_score=validated_score)

def append(path,row):
    with path.open('a') as f:f.write(canonical(row)+'\n');f.flush();os.fsync(f.fileno())

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',type=Path,required=True)
    p.add_argument('--data',type=Path,default=ROOT/'data/study/pilot-v5')
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--execute',action='store_true')
    p.add_argument('--approved-usd-limit',type=Decimal)
    p.add_argument('--resume',action='store_true')
    a=p.parse_args();cfg=json.loads(a.config.read_text());data=json.loads((a.data/'inputs.json').read_text())
    planned=prepare(cfg,data)
    manifest=dict(created_at=now(),scope='development fixed-context pilot; not market or commercial validation',
        config=cfg,data_sha256=sha((a.data/'inputs.json').read_bytes()),planned=planned,
        max_planned_input_tokens=cfg['max_input_tokens']*len(planned),
        max_planned_output_tokens=cfg['max_output_tokens']*len(planned),
        all_contexts_identical_within_case=True,
        maximum_input_upper_bound=max(r['input_token_upper_bound'] for r in planned),
        source_sha256=sha(Path(__file__).read_bytes()),executed=False,
        dependency_sha256={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in
            [ROOT/'study/contract.py',ROOT/'study/retrieval.py']},
        verified_billed_cost_usd=None)
    if not a.execute:
        a.output.mkdir(parents=True,exist_ok=False)
        (a.output/'plan.json').write_text(json.dumps(manifest,indent=2)+'\n')
        print(json.dumps({k:manifest[k] for k in ['executed','max_planned_input_tokens','max_planned_output_tokens','maximum_input_upper_bound']}))
        return
    if a.approved_usd_limit is None or not a.approved_usd_limit.is_finite() or a.approved_usd_limit<=0:
        raise ValueError('explicit positive user-approved USD ceiling is required')
    if len(planned)>cfg['max_requests'] or not all(r['within_input_bound'] for r in planned):
        raise ValueError('pilot exceeds configured request/input caps')
    for provider in cfg['providers']:
        if not provider.get('model') or not provider.get('price_source') or not provider.get('price_checked_at'):
            raise ValueError('exact model ID and dated verified price source required')
        for key in ['input_usd_per_million','output_usd_per_million']:
            value=Decimal(str(provider.get(key)))
            if not value.is_finite() or value<0:raise ValueError('invalid price rate')
        if not api_key(provider['provider']):raise ValueError('credential missing: '+KEYS[provider['provider']])
    if not a.resume:a.output.mkdir(parents=True,exist_ok=False)
    lock=(a.output/'.run.lock').open('a')
    try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:raise ValueError('another runner owns this output directory')
    log=a.output/'attempts.jsonl';old=[]
    if a.resume:
        previous=json.loads((a.output/'manifest.json').read_text())
        if any(previous[k]!=manifest[k] for k in ['config','data_sha256','planned','source_sha256','dependency_sha256']):
            raise ValueError('resume differs from frozen plan/source')
        old=[json.loads(s) for s in log.read_text().splitlines()] if log.exists() else []
    manifest.update(executed=True,approved_usd_limit=str(a.approved_usd_limit),status='running')
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    # Keep each full preflight reservation, even after a failure. Conservative
    # accounting bounds exposure without assuming a timeout was free.
    started={r['id']:r for r in old if r['status']=='issued'}
    terminal={r['id'] for r in old if r['status'] in ['completed','failed','interrupted']}
    for identity in sorted(set(started)-terminal):
        append(log,dict(id=identity,status='interrupted',at=now(),usage=None,
                        note='issued without terminal response; full reservation retained; never retried'))
    reserved=sum((Decimal(r['reserved_usd']) for r in started.values()),Decimal(0))
    worlds={w['id']:w for w in data['worlds']};cases={c['id']:c for c in data['queries']}
    providers={p['provider']:p for p in cfg['providers']}
    for plan in planned:
        if plan['id'] in started:continue
        hold=Decimal(plan['reserved_usd'])
        if reserved+hold>a.approved_usd_limit:
            manifest['status']='budget_exhausted';break
        provider=providers[plan['provider']];reqbody=payload(provider,plan['messages'],cfg['max_output_tokens'])
        headers={'Content-Type':'application/json'}
        if plan['provider']=='openai':headers['Authorization']='Bearer '+api_key('openai')
        else:headers.update({'x-api-key':api_key('anthropic'),'anthropic-version':'2023-06-01'})
        folder=a.output/plan['id'];folder.mkdir(exist_ok=False)
        (folder/'request.json').write_text(canonical(reqbody)+'\n')
        append(log,dict(id=plan['id'],status='issued',at=now(),reserved_usd=str(hold)))
        reserved+=hold
        row=dict(id=plan['id'],at=now(),status='failed',billed_cost_usd=None)
        start=time.perf_counter()
        try:
            req=urllib.request.Request(ENDPOINTS[plan['provider']],data=canonical(reqbody).encode(),headers=headers)
            with urllib.request.urlopen(req,timeout=180) as response:raw=response.read(16*1024*1024)
            (folder/'response.json').write_bytes(raw)
            response=json.loads(raw);text,usage,finish,complete=decode(plan['provider'],response)
            row.update(usage=usage,finish_reason=finish,response_model=response.get('model'),response_id=response.get('id'))
            if not complete:raise ValueError('incomplete provider output')
            if not isinstance(usage.get('input_tokens'),int) or not isinstance(usage.get('output_tokens'),int):
                raise ValueError('missing usage; reservation retained')
            estimated=cost(provider,usage['input_tokens'],usage['output_tokens'])
            row['estimated_cost_usd']=str(estimated)
            if (usage['input_tokens']>plan['input_token_upper_bound'] or usage['output_tokens']>cfg['max_output_tokens']
                or usage.get('cache_creation_input_tokens',0)):
                manifest['status']='unexpected_usage_stop';raise ValueError('usage outside conservative accounting assumption')
            case=cases[plan['case_id']];world=worlds[case['query']['world']]
            evidence=[e for e in world['events'] if e['id'] in plan['evidence_ids']]
            row.update(evaluate(text,case,world,evidence),status='completed')
        except Exception as exc:
            # Do not store headers or credentials, even in transport errors.
            row.update(error_type=type(exc).__name__,error_code=getattr(exc,'code',None))
        row.update(finished_at=now(),elapsed_seconds=time.perf_counter()-start)
        append(log,row)
        print(json.dumps({'id':plan['id'],'status':row['status'],'reserved_usd':str(reserved)}),flush=True)
        if manifest.get('status')=='unexpected_usage_stop':break
    else:manifest['status']='plan_exhausted'
    manifest.update(finished_at=now(),reserved_usd=str(reserved))
    final=[json.loads(s) for s in log.read_text().splitlines()] if log.exists() else []
    manifest['counts']={state:sum(r['status']==state for r in final)
                        for state in ['issued','completed','failed','interrupted']}
    manifest['unstarted']=len(planned)-manifest['counts']['issued']
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    lock.close()

if __name__=='__main__':main()
