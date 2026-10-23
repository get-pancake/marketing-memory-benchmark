"""One real format/settings check per provider; preserve every attempt."""
import json, os, sys, time, urllib.request, urllib.error
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from benchmarks.recommendation.run import now, decode
from benchmarks.integrated.run import usage_cost

def main():
    cfg=json.loads(Path('benchmarks/challenge/providers.json').read_text())
    out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
    schema={'type':'object','properties':{'ready':{'type':'boolean'}},'required':['ready'],'additionalProperties':False}
    for p in cfg['providers']:
        name=p['provider']; start=time.perf_counter()
        if name=='openai':
            body={'model':p['model'],'input':[{'role':'user','content':'Return ready true.'}], 'max_output_tokens':512,'store':False,
                  'reasoning':{'effort':'medium'},'text':{'format':{'type':'json_schema','name':'readiness','strict':True,'schema':schema}}}
            url='https://api.openai.com/v1/responses';headers={'Authorization':'Bearer '+os.environ['RESEARCH_OPENAI_API_KEY']}
        else:
            body={'model':p['model'],'messages':[{'role':'user','content':'Return ready true.'}],'max_tokens':512,
                  'thinking':{'type':'adaptive'},'output_config':{'effort':'high','format':{'type':'json_schema','schema':schema}}}
            url='https://api.anthropic.com/v1/messages';headers={'x-api-key':os.environ['RESEARCH_ANTHROPIC_API_KEY'],'anthropic-version':'2023-06-01'}
        headers['Content-Type']='application/json'
        (out/(name+'-request.json')).write_text(json.dumps(body,indent=2)+'\n')
        receipt={'provider':name,'requested_model':p['model'],'started_at':now(),'status':'failed'}
        try:
            with urllib.request.urlopen(urllib.request.Request(url,data=json.dumps(body).encode(),headers=headers),timeout=180) as r:raw=r.read()
            (out/(name+'-response.json')).write_bytes(raw)
            obj=json.loads(raw);text,usage,finish,complete=decode(name,obj)
            receipt.update(status='completed' if complete else 'incomplete',model=obj.get('model'),usage=usage,finish=finish,
                           accounting=usage_cost(name,usage,p),parsed=json.loads(text))
        except urllib.error.HTTPError as e:receipt.update(error_type='HTTPError',http_status=e.code)
        except Exception as e:receipt.update(error_type=type(e).__name__)
        receipt.update(seconds=time.perf_counter()-start,finished_at=now())
        (out/(name+'-receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)

if __name__=='__main__':main()
