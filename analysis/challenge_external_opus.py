"""Replay fixed external contexts with actual Opus; separate exploratory evidence."""
import argparse,json,sys,random
from concurrent.futures import ThreadPoolExecutor,as_completed
from decimal import Decimal
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from benchmarks.challenge.core import canonical,sha,dump
from benchmarks.integrated.external_wiki import call,now,SOURCE
from benchmarks.integrated.external_evaluate import matches
from benchmarks.recommendation.run import decode
from benchmarks.integrated.run import usage_cost

ROOT=Path(__file__).resolve().parents[1]
def plans():
    cfg=json.loads((ROOT/'benchmarks/challenge/providers.json').read_text());provider=next(x for x in cfg['providers'] if x['provider']=='anthropic');out=[]
    for version in ['external-reader-v1','external-chunks-v1']:
        manifest=json.loads((ROOT/'experiments/integrated'/version/'manifest.json').read_text())
        for prior in manifest['planned']:
            if prior['provider']!='anthropic':continue
            row=dict(prior);body=json.loads(canonical(prior['body']));body.update(model=provider['model'],max_tokens=8192,thinking={'type':'adaptive'})
            body['output_config']={**body['output_config'],'effort':'high'}
            reserve=(Decimal(len(canonical(body).encode())+4096)*8+Decimal(8192)*20)/Decimal(1000000)
            row.update(body=body,reserved_usd=str(reserve),original_manifest='experiments/integrated/'+version+'/manifest.json',original_body_sha256=sha(canonical(prior['body']).encode()))
            out.append(row)
    random.Random(20261023045).shuffle(out);return provider,out

def labels():return {r['id']:r for r in map(json.loads,(SOURCE/'labels/agent-tasks/dev.jsonl').read_text().splitlines())}
def execute(output,cap,workers):
    provider,planned=plans();total=sum((Decimal(x['reserved_usd']) for x in planned),Decimal(0))
    if total>cap:raise ValueError('entire extension exceeds operational guard')
    output.mkdir(parents=True,exist_ok=False);truth=labels()
    manifest={'status':'running','created_at':now(),'provider':provider,'planned':planned,'reserved_usd':str(total),'operational_cap_usd':str(cap),'user_numeric_budget':None,
              'scope':'Exploratory fixed-context Opus extension; one externally authored fictional company, development questions already inspected; no new independent-company evidence.',
              'source_sha256':{str(f.relative_to(ROOT)):sha(f.read_bytes()) for f in [Path(__file__).resolve(),ROOT/'benchmarks/integrated/external_evaluate.py',ROOT/'benchmarks/integrated/external_wiki.py']}}
    dump(output/'manifest.json',manifest);terminal=[]
    def one(plan):
        row=call(provider,plan['body'],output/plan['id']);row.update({k:plan[k] for k in ['id','case_id','arm','context_bytes']});row.update(answer_correct=False,citation_ids_valid=False)
        if row['status']=='completed':
            try:
                parsed=json.loads(row['text']);row.update(output=parsed,answer_correct=matches(parsed['answer'],truth[plan['case_id']]),citation_ids_valid=all(x in plan['source_ids'] for x in parsed['citations']))
            except Exception as e:row.update(status='failed',error_type=type(e).__name__)
        dump(output/plan['id']/'evaluated.json',row);return row
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for offset in range(0,len(planned),workers):
            wave=planned[offset:offset+workers]
            with (output/'attempts.jsonl').open('a') as f:
                for x in wave:f.write(canonical({'id':x['id'],'status':'issued','at':now()})+'\n')
            stop=False
            for fut in as_completed([pool.submit(one,x) for x in wave]):
                row=fut.result();terminal.append(row)
                with (output/'attempts.jsonl').open('a') as f:f.write(canonical(row)+'\n')
                stop|=row.get('http_status') in [401,403,429]
                print(canonical({'id':row['id'],'status':row['status']}),flush=True)
            if stop:manifest['status']='provider_stop';break
        else:manifest['status']='completed'
    manifest.update(finished_at=now(),attempted=len(terminal),completed=sum(r['status']=='completed' for r in terminal));dump(output/'manifest.json',manifest)

def analyze(run,output):
    m=json.loads((run/'manifest.json').read_text());truth=labels();rows=[];provider=m['provider'];expected_provider,expected_plans=plans()
    if m['planned']!=expected_plans or provider!=expected_provider:raise ValueError('extension differs from declared replay')
    for p in m['planned']:
        folder=run/p['id'];row=json.loads((folder/'evaluated.json').read_text())
        if json.loads((folder/'request.json').read_text())!=p['body']:raise ValueError('request differs')
        if row['status']=='completed':
            obj=json.loads((folder/'response.json').read_text());text,usage,_,complete=decode('anthropic',obj)
            if not complete or json.loads(text)!=row['output'] or matches(json.loads(text)['answer'],truth[p['case_id']])!=row['answer_correct']:raise ValueError('raw answer score mismatch')
            if usage_cost('anthropic',usage,provider)!=row['accounting']:raise ValueError('usage accounting differs')
        rows.append(row)
    summary={'status':m['status'],'calls':len(rows),'completed':sum(r['status']=='completed' for r in rows),'model':provider['model'],'independent_companies':1,
             'exposed_development_questions':22,'new_inference_not_new_test_data':True,'groups':{},'scope':m['scope']}
    for arm in sorted({r['arm'] for r in rows}):
        xs=[r for r in rows if r['arm']==arm];sensitive=[r for r in xs if r['case_id']!='dev-op-2']
        summary['groups'][arm]={'cases':len(xs),'correct':sum(r['answer_correct'] for r in xs),'citation_ids_valid':sum(r['citation_ids_valid'] for r in xs),
              'excluding_ambiguous_label_correct':sum(r['answer_correct'] for r in sensitive),'excluding_ambiguous_label_cases':len(sensitive),
              'estimated_usd':str(sum((Decimal(r.get('accounting',{}).get('estimated_usd','0')) for r in xs),Decimal(0)))}
    output.mkdir(parents=True,exist_ok=True);dump(output/'summary.json',summary);dump(output/'per-attempt.json',rows);print(canonical(summary))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--analyze',type=Path);p.add_argument('--execute',action='store_true');p.add_argument('--operational-cap-usd',type=Decimal,default=Decimal(175));p.add_argument('--workers',type=int,default=16);a=p.parse_args()
    if a.analyze:analyze(a.analyze,a.output)
    elif a.execute:execute(a.output,a.operational_cap_usd,a.workers)
    else:
        _,xs=plans();print(canonical({'planned_calls':len(xs),'reserved_usd':str(sum((Decimal(x['reserved_usd']) for x in xs),Decimal(0))),'executed':False}))
