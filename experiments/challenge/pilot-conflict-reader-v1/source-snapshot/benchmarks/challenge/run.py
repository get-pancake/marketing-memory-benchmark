"""Capped real API experiment; immutable requests, no retries or answer repair."""
import argparse,fcntl,json,os,random,sys,time,urllib.request,urllib.error
from concurrent.futures import ThreadPoolExecutor,as_completed
from decimal import Decimal
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from benchmarks.challenge.core import canonical,sha,dump,score,visible,output_schema
from benchmarks.recommendation.run import decode,now
from benchmarks.integrated.run import usage_cost

ROOT=Path(__file__).resolve().parents[2]
KEYS={'openai':'RESEARCH_OPENAI_API_KEY','anthropic':'RESEARCH_ANTHROPIC_API_KEY'}
URLS={'openai':'https://api.openai.com/v1/responses','anthropic':'https://api.anthropic.com/v1/messages'}
def body(provider,packet,q,limit):
    msg=packet['messages'];schema=output_schema(q)
    if provider['provider']=='openai':
        return {'model':provider['model'],'input':msg,'max_output_tokens':limit,'store':False,**provider['request_options'],
                'text':{'format':{'type':'json_schema','name':'marketing_plan','strict':True,'schema':schema}}}
    obj={'model':provider['model'],'system':msg[0]['content'],'messages':[msg[1]],'max_tokens':limit,**provider['request_options']}
    obj['output_config']={**obj.get('output_config',{}),'format':{'type':'json_schema','schema':schema}};return obj
def append(path,row):
    with path.open('a') as f:f.write(canonical(row)+'\n');f.flush();os.fsync(f.fileno())

def main():
    p=argparse.ArgumentParser();
    for name in ['data','packets','config','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--execute',action='store_true');p.add_argument('--resume',action='store_true');p.add_argument('--workers',type=int,default=12)
    p.add_argument('--operational-cap-usd',type=Decimal);a=p.parse_args();cfg=json.loads(a.config.read_text())
    index=json.loads((a.data/'index.json').read_text());cases={};packets={};plans=[]
    for entry in index['cases']:
        case=json.loads((a.data/entry['path']).read_text())
        if sha((a.data/entry['path']).read_bytes())!=entry['sha256']:raise ValueError('data hash mismatch')
        cases[case['id']]=case;path=a.packets/case['id']/'packets.json'
        for packet in json.loads(path.read_text()):
            packets[(case['id'],packet['arm'])]=packet
            for provider in cfg['providers']:
                upper=sum(len(m['content'].encode()) for m in packet['messages'])+len(canonical(output_schema(case['query'])).encode())+4096
                reserve=(Decimal(upper)*Decimal(str(provider['reservation_input_usd_per_million']))+Decimal(cfg['max_output_tokens'])*Decimal(str(provider['output_usd_per_million'])))/Decimal(1000000)
                plans.append({'id':case['id']+'-'+provider['provider']+'-'+packet['arm'],'case_id':case['id'],'world':case['world'],'family':case['family'],'level':case['level'],'provider':provider['provider'],'arm':packet['arm'],'packet_sha256':sha(path.read_bytes()),'reserved_usd':str(reserve),'input_upper_bound':upper})
    random.Random(cfg['order_seed']).shuffle(plans)
    hashes={str(f.relative_to(ROOT)):sha(f.read_bytes()) for f in sorted((ROOT/'benchmarks/challenge').glob('*.py'))}
    hashes.update({str(f.relative_to(ROOT)):sha(f.read_bytes()) for f in [ROOT/'benchmarks/recommendation/run.py',ROOT/'benchmarks/integrated/run.py']})
    manifest={'created_at':now(),'config':cfg,'data_index_sha256':sha((a.data/'index.json').read_bytes()),'packets_manifest_sha256':sha((a.packets/'manifest.json').read_bytes()),'source_sha256':hashes,'planned':plans,'reservation_total_usd':str(sum((Decimal(x['reserved_usd']) for x in plans),Decimal(0))),'executed':False,'user_numeric_budget':None,'cap_authority':'Researcher-selected guard under explicit API execution authorization; not a user-specified limit.','status':'planned'}
    if not a.execute:
        a.output.mkdir(parents=True,exist_ok=False);dump(a.output/'plan.json',manifest);print(canonical({'requests':len(plans),'reserved_usd':manifest['reservation_total_usd']}));return
    if a.operational_cap_usd is None or Decimal(manifest['reservation_total_usd'])>a.operational_cap_usd:raise ValueError('entire experiment exceeds operational guard')
    if len(plans)>cfg['max_requests'] or max(x['input_upper_bound'] for x in plans)>cfg['max_input_upper_bound']:raise ValueError('configured envelope exceeded')
    for provider in cfg['providers']:
        if not os.environ.get(KEYS[provider['provider']]):raise ValueError('missing provider credential')
    if not a.resume:a.output.mkdir(parents=True,exist_ok=False)
    lock=(a.output/'.run.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    ledger=a.output/'attempts.jsonl';old=[]
    if a.resume:
        prior=json.loads((a.output/'manifest.json').read_text())
        for k in ['config','data_index_sha256','packets_manifest_sha256','source_sha256','planned']:
            if prior[k]!=manifest[k]:raise ValueError('resume changed '+k)
        old=[json.loads(s) for s in ledger.read_text().splitlines()] if ledger.exists() else []
    started={r['id'] for r in old if r['status']=='issued'};done={r['id'] for r in old if r['status'] in ['completed','failed','interrupted']}
    for identity in sorted(started-done):
        result=a.output/identity/'result.json'
        if result.exists():
            terminal=json.loads(result.read_text());terminal['recovered_from_saved_result']=True;append(ledger,terminal)
        else:append(ledger,{'id':identity,'status':'interrupted','at':now(),'note':'No automatic reissue; full reserved cost retained.'})
    manifest.update(status='running',executed=True,operational_cap_usd=str(a.operational_cap_usd));dump(a.output/'manifest.json',manifest)
    if not a.resume:
        for source,digest in hashes.items():
            target=a.output/'source-snapshot'/source;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/source).read_bytes())
    providers={p['provider']:p for p in cfg['providers']}
    def call(plan):
        folder=a.output/plan['id'];folder.mkdir();provider=providers[plan['provider']];case=cases[plan['case_id']];packet=packets[(case['id'],plan['arm'])]
        payload=body(provider,packet,case['query'],cfg['max_output_tokens']);dump(folder/'request.json',payload)
        headers={'Content-Type':'application/json'}
        if plan['provider']=='openai':headers['Authorization']='Bearer '+os.environ[KEYS['openai']]
        else:headers.update({'x-api-key':os.environ[KEYS['anthropic']],'anthropic-version':'2023-06-01'})
        row={k:plan[k] for k in ['id','case_id','world','family','level','provider','arm']};row.update(status='failed',started_at=now(),evidence_bytes=packet['evidence_bytes']);start=time.perf_counter()
        try:
            req=urllib.request.Request(URLS[plan['provider']],data=canonical(payload).encode(),headers=headers)
            with urllib.request.urlopen(req,timeout=240) as response:
                raw=response.read(16*1024*1024);row['rate_limit_headers']={k:v for k,v in response.headers.items() if 'ratelimit' in k.lower()}
            (folder/'response.json').write_bytes(raw);obj=json.loads(raw);text,usage,finish,complete=decode(plan['provider'],obj)
            row.update(response_model=obj.get('model'),response_id=obj.get('id'),usage=usage,finish_reason=finish,accounting=usage_cost(plan['provider'],usage,provider))
            if row['accounting']['total_input_tokens']>plan['input_upper_bound'] or row['accounting']['output_tokens']>cfg['max_output_tokens']:raise ValueError('usage bound exceeded')
            if not complete:raise ValueError('incomplete generation')
            parsed=json.loads(text)
            if set(parsed)!={'actions','reasoning_summary','missing'} or not isinstance(parsed['actions'],list):raise ValueError('schema mismatch')
            evidence=[e for e in visible(case['events'],case['query']) if e['id'] in packet['evidence_ids']]
            row.update(output=parsed,score=score(parsed,case,evidence),status='completed')
        except urllib.error.HTTPError as e:row.update(error_type='HTTPError',http_status=e.code)
        except Exception as e:row.update(error_type=type(e).__name__)
        row.update(finished_at=now(),seconds=time.perf_counter()-start);dump(folder/'result.json',row);return row
    pending=[p for p in plans if p['id'] not in started]
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        for offset in range(0,len(pending),a.workers):
            wave=pending[offset:offset+a.workers]
            for item in wave:append(ledger,{'id':item['id'],'status':'issued','at':now(),'reserved_usd':item['reserved_usd']})
            stop=False
            for future in as_completed([pool.submit(call,x) for x in wave]):
                row=future.result();append(ledger,row);stop|=row.get('http_status') in [401,403,429]
                print(canonical({'id':row['id'],'status':row['status'],'seconds':round(row['seconds'],2),'cost':row.get('accounting',{}).get('estimated_usd')}),flush=True)
            if stop:manifest['status']='provider_stop';break
        else:manifest['status']='completed'
    terminal=[json.loads(s) for s in ledger.read_text().splitlines() if json.loads(s)['status'] in ['completed','failed','interrupted']]
    manifest.update(finished_at=now(),attempted=len(terminal),successful=sum(x['status']=='completed' for x in terminal),estimated_usage_cost_usd=str(sum((Decimal(x.get('accounting',{}).get('estimated_usd','0')) for x in terminal),Decimal(0))))
    dump(a.output/'manifest.json',manifest)

if __name__=='__main__':main()
