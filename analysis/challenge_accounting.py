"""Count physical provider attempts once, including recovered embedding responses."""
import argparse,gzip,json,sys
from decimal import Decimal
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from benchmarks.challenge.core import dump,sha,canonical
from benchmarks.integrated.run import usage_cost

ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    cfg=json.loads((ROOT/'benchmarks/challenge/providers.json').read_text());providers={p['provider']:p for p in cfg['providers']};records=[];seen=set();unknown=[]
    for run in ['pilot-reader-v1','pilot-conflict-reader-v1','main-reader-v1']:
        folder=ROOT/'experiments/challenge'/run;manifest=json.loads((folder/'manifest.json').read_text())
        for plan in manifest['planned']:
            path=folder/plan['id']/'response.json';result_path=folder/plan['id']/'result.json'
            if path.exists():
                obj=json.loads(path.read_text());identity=obj['id']
                if identity in seen:raise ValueError('generation response counted twice')
                seen.add(identity);account=usage_cost(plan['provider'],obj['usage'],providers[plan['provider']])
                records.append({'kind':'generation','phase':run,'provider':plan['provider'],'response_id':identity,'path':str(path.relative_to(ROOT)),'estimated_usd':account['estimated_usd'],'input_tokens':account['total_input_tokens'],'output_tokens':account['output_tokens']})
            else:unknown.append({'phase':run,'id':plan['id'],'note':'No raw usage response; possible billing cannot be inferred from local failure.'})
    for provider in providers:
        path=ROOT/'experiments/challenge/provider-smoke-v1'/(provider+'-response.json');obj=json.loads(path.read_text());account=usage_cost(provider,obj['usage'],providers[provider])
        if obj['id'] in seen:raise ValueError('duplicate availability response')
        seen.add(obj['id']);records.append({'kind':'generation','phase':'availability','provider':provider,'response_id':obj['id'],'path':str(path.relative_to(ROOT)),'estimated_usd':account['estimated_usd'],'input_tokens':account['total_input_tokens'],'output_tokens':account['output_tokens']})
    extension=ROOT/'experiments/challenge/external-opus-v1'
    for plan in json.loads((extension/'manifest.json').read_text())['planned']:
        path=extension/plan['id']/'response.json'
        if not path.exists():unknown.append({'phase':'external-opus-v1','id':plan['id'],'note':'No saved usage response.'});continue
        obj=json.loads(path.read_text());identity=obj['id']
        if identity in seen:raise ValueError('external response counted twice')
        seen.add(identity);account=usage_cost('anthropic',obj['usage'],providers['anthropic'])
        records.append({'kind':'generation','phase':'external-opus-v1','provider':'anthropic','response_id':identity,'path':str(path.relative_to(ROOT)),'estimated_usd':account['estimated_usd'],'input_tokens':account['total_input_tokens'],'output_tokens':account['output_tokens']})
    for path in sorted((ROOT/'experiments/challenge').glob('*/embedding-*/request.json')):
        response=path.with_name('response.json.gz')
        if not response.exists():unknown.append({'phase':path.parent.parent.name,'path':str(path.relative_to(ROOT)),'note':'Embedding attempt has no saved usage response.'});continue
        obj=json.loads(gzip.decompress(response.read_bytes()));req=json.loads(path.read_text())
        if req['model']!='text-embedding-3-small' or obj['model']!='text-embedding-3-small':raise ValueError('unpriced embedding model')
        cost=Decimal(obj['usage']['total_tokens'])*Decimal('.02')/Decimal(1000000)
        records.append({'kind':'embedding','phase':path.parent.parent.name,'provider':'openai','path':str(response.relative_to(ROOT)),'response_sha256':sha(response.read_bytes()),'estimated_usd':str(cost),'input_tokens':obj['usage']['total_tokens'],'output_tokens':0})
    totals={}
    for phase in sorted({r['phase'] for r in records}):
        rows=[r for r in records if r['phase']==phase]
        totals[phase]={'physical_responses':len(rows),'estimated_usd':str(sum((Decimal(r['estimated_usd']) for r in rows),Decimal(0))),'input_tokens':sum(r['input_tokens'] for r in rows),'output_tokens':sum(r['output_tokens'] for r in rows)}
    result={'scope':'Challenge/v4 only; includes availability, both development readers, all raw main attempts and actual embeddings. Reused vectors and aliased query-word controls are not additional calls. Prior v3 costs are separately retained.',
            'generation_responses':sum(r['kind']=='generation' for r in records),'embedding_responses':sum(r['kind']=='embedding' for r in records),'known_estimated_usd':str(sum((Decimal(r['estimated_usd']) for r in records),Decimal(0))),
            'unknown_usage_attempts':unknown,'invoice_verified':False,'hardware_and_maintenance_cost_included':False,'phases':totals,'records':records}
    dump(a.output,result);print(canonical({k:result[k] for k in ['generation_responses','embedding_responses','known_estimated_usd','unknown_usage_attempts']}))

if __name__=='__main__':main()
