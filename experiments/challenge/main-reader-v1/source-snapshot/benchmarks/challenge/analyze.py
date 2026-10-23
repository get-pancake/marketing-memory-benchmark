"""Recompute every outcome from saved raw responses; company-clustered inference."""
import argparse,csv,json,math,statistics,sys
from collections import defaultdict,Counter
from decimal import Decimal
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from benchmarks.challenge.core import canonical,sha,dump,score,visible,gold
from benchmarks.challenge.retrieve import ARMS,select
from benchmarks.recommendation.run import decode
from benchmarks.integrated.run import usage_cost

def bootstrap(values,strata,rng,reps=10000):
    parts=[]
    for group in sorted(set(strata)):
        ids=np.array([i for i,s in enumerate(strata) if s==group]);parts.append(rng.choice(ids,size=(reps,len(ids)),replace=True))
    draws=np.concatenate(parts,axis=1);return values[draws].mean(axis=1)

def analyze(data,packets,run,out):
    out.mkdir(parents=True,exist_ok=True);idx=json.loads((data/'index.json').read_text());manifest=json.loads((run/'manifest.json').read_text())
    providers={p['provider']:p for p in manifest['config']['providers']};cases={e['id']:json.loads((data/e['path']).read_text()) for e in idx['cases']}
    plans=manifest['planned'];records=[];reconstructed=0;raw_checked=0
    packetmap={};contexts=[]
    for cid,case in cases.items():
        receipt=json.loads((packets/cid/'receipt.json').read_text());ev=visible(case['events'],case['query'])
        for packet in json.loads((packets/cid/'packets.json').read_text()):
            ranks=receipt['markdown_ranking'] if packet['arm']=='markdown' else receipt['gbrain_ranking']
            selected=select(ev,case['query'],ranks,packet['arm'],case['budget_bytes'])
            if [e['id'] for e in selected]!=packet['evidence_ids']:raise ValueError('context reconstruction differs')
            packetmap[(cid,packet['arm'])]=(packet,selected);reconstructed+=1
            context=score({'actions':[]},case,selected)
            contexts.append({'case_id':cid,'world':case['world'],'family':case['family'],'level':case['level'],'arm':packet['arm'],'optimum':context['optimum'],'recoverable_value':context['recoverable_value'],'normalized_value':context['context_normalized_value'],'evidence_bytes':packet['evidence_bytes']})
    for plan in plans:
        folder=run/plan['id'];result=json.loads((folder/'result.json').read_text()) if (folder/'result.json').exists() else {'status':'not_completed'}
        case=cases[plan['case_id']];packet,evidence=packetmap[(case['id'],plan['arm'])];reference=gold(case)
        if sha((packets/case['id']/'packets.json').read_bytes())!=plan['packet_sha256']:raise ValueError('packet hash mismatch')
        sc=score({'actions':[]},case,evidence);sc.update(normalized_value=0.0 if reference['optimum'] else None,returned_value=0,exact_optimum=False,actionable=False,abstained=False,unsafe=False)
        if result['status']=='completed':
            obj=json.loads((folder/'response.json').read_text());text,usage,finish,complete=decode(plan['provider'],obj)
            if not complete:raise ValueError('saved completed status inconsistent')
            calculated=score(json.loads(text),case,evidence)
            if calculated!=result['score'] or json.loads(text)!=result['output']:raise ValueError('raw response score differs')
            if usage_cost(plan['provider'],usage,providers[plan['provider']])!=result['accounting']:raise ValueError('cost reconstruction differs')
            sc=calculated;raw_checked+=1
        records.append({**{k:plan[k] for k in ['id','case_id','world','family','level','arm','provider']},**sc,'status':result['status'],'seconds':result.get('seconds'),
                        'estimated_usd':float(result.get('accounting',{}).get('estimated_usd',0)),
                        'input_tokens':result.get('accounting',{}).get('total_input_tokens',0),'output_tokens':result.get('accounting',{}).get('output_tokens',0),'evidence_bytes':packet['evidence_bytes']})
    def aggregate(xs,metric):
        by=defaultdict(list)
        for r in xs:
            if r[metric] is not None:by[r['world']].append(r[metric])
        return {w:float(np.mean(v)) for w,v in by.items()}
    world_family={c['world']:c['family'] for c in cases.values()};rng=np.random.default_rng(20261023044);summary=[];contrasts=[]
    for provider in providers:
        methods={}
        for arm in ARMS:
            rows=[r for r in records if r['provider']==provider and r['arm']==arm];vals=aggregate(rows,'normalized_value');methods[arm]=vals
            worlds=sorted(vals);v=np.array([vals[w] for w in worlds]);strata=[world_family[w] for w in worlds];boot=bootstrap(v,strata,rng)
            positive=[r for r in rows if r['optimum']>0];negative=[r for r in rows if not r['optimum']]
            summary.append({'provider':provider,'model':providers[provider]['model'],'arm':arm,'worlds':len(v),'cases':len(rows),'positive_cases':len(positive),'negative_cases':len(negative),
                'mean_normalized_value':float(v.mean()),'ci95':np.quantile(boot,[.025,.975]).tolist(),'context_value':float(np.mean(list(aggregate([x for x in contexts if x['arm']==arm],'normalized_value').values()))),
                'exact_positive':sum(r['exact_optimum'] for r in positive),'actionable_positive':sum(r['actionable'] for r in positive),
                'unsafe_all':sum(r['unsafe'] for r in rows),'unsafe_negative':sum(r['unsafe'] for r in negative),'safe_negative':sum(r['status']=='completed' and r['exact_optimum'] for r in negative),
                'abstained_positive':sum(r['abstained'] for r in positive),'failed':sum(r['status']!='completed' for r in rows),
                'estimated_usd':sum(r['estimated_usd'] for r in rows),'mean_seconds':float(np.mean([r['seconds'] for r in rows if r['seconds'] is not None])),
                'input_tokens':sum(r['input_tokens'] for r in rows),'output_tokens':sum(r['output_tokens'] for r in rows),
                'by_level':{level:{'cases':len([r for r in rows if r['level']==level]),'positive_cases':len([r for r in positive if r['level']==level]),
                            'mean_normalized_value':float(np.mean([r['normalized_value'] for r in positive if r['level']==level])),
                            'context_value':float(np.mean([x['normalized_value'] for x in contexts if x['level']==level and x['arm']==arm and x['normalized_value'] is not None]))} for level in ['accessible','constrained','stress']}})
        for control in ['company','markdown','gbrain','none','full']:
            worlds=sorted(methods['gtm']);d=np.array([methods['gtm'][w]-methods[control][w] for w in worlds]);strata=[world_family[w] for w in worlds]
            b=bootstrap(d,strata,rng);signs=rng.choice([-1,1],size=(10000,len(d)))
            p=(1+int(np.sum(np.abs((signs*d).mean(axis=1))>=abs(float(d.mean()))-1e-12)))/10001
            contrasts.append({'provider':provider,'treatment':'gtm','control':control,'difference':float(d.mean()),'ci95':np.quantile(b,[.025,.975]).tolist(),'world_sd':float(d.std(ddof=1)),
                              'worlds_improved':int(np.sum(d>1e-12)),'worlds_tied':int(np.sum(abs(d)<=1e-12)),'worlds_worse':int(np.sum(d< -1e-12)),
                              'random_sign_p':p,'confirmatory':control=='company'})
    primary=sorted([c for c in contrasts if c['confirmatory']],key=lambda c:c['random_sign_p']);last=0
    for i,c in enumerate(primary):last=max(last,min(1,c['random_sign_p']*(len(primary)-i)));c['holm_p']=last
    for name,rows in [('per-attempt',records),('context',contexts)]:
        dump(out/(name+'.json'),rows)
        with (out/(name+'.csv')).open('w') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    maxsd=max(c['world_sd'] for c in primary);calculated=math.ceil(((1.96*maxsd/.05)**2)/3)*3;selected=max(120,min(192,calculated))
    res={'status':'passed','worlds':idx['worlds'],'cases':len(cases),'attempts':len(records),'completed':raw_checked,'failed':len(records)-raw_checked,'reconstructed_context_packets':reconstructed,
         'estimated_usage_usd':str(sum((Decimal(str(r['estimated_usd'])) for r in records),Decimal(0))),
         'primary_unit':'equal-company mean of normalized grounded policy value on positive cases; bootstrap companies stratified by administrative sector labels',
         'independent_human_validation':False,'summary':summary,'contrasts':contrasts,
         'precision_rule':{'pilot_max_world_sd':maxsd,'raw_required_rounded':calculated,'selected_main_worlds':selected,'minimum':120,'maximum':192,'target_halfwidth':.05},
         'source_hashes':{'data_index':sha((data/'index.json').read_bytes()),'run_manifest':sha((run/'manifest.json').read_bytes())}}
    dump(out/'summary.json',res);print(canonical({k:res[k] for k in ['worlds','cases','attempts','completed','failed','estimated_usage_usd','precision_rule']}))
    return res

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ['data','packets','run','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();analyze(a.data,a.packets,a.run,a.output)
