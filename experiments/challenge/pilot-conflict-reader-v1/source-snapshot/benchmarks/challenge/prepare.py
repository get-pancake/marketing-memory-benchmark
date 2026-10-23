"""Actual common embeddings, native GBrain search and label-blind context export."""
import argparse,base64,gzip,json,math,os,sqlite3,struct,subprocess,sys,time,urllib.request
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from benchmarks.challenge.core import canonical,sha,dump,visible,event_text,query_text,messages,source_view
from benchmarks.challenge.retrieve import ARMS,select,rank_hybrid

ROOT=Path(__file__).resolve().parents[2];PIN='531b3b1ab66c88f192abb51338028c44b80fbf21'
def now():return datetime.now(timezone.utc).isoformat()
def zipped(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('wb') as f:
        with gzip.GzipFile(fileobj=f,mode='wb',mtime=0) as z:z.write(raw)

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--cache',type=Path,default=ROOT/'.cache/challenge-embeddings.sqlite');p.add_argument('--execute-embeddings',action='store_true')
    p.add_argument('--workers',type=int,default=2);p.add_argument('--resume',action='store_true');a=p.parse_args()
    if not a.resume:a.output.mkdir(parents=True,exist_ok=False)
    upstream=ROOT/'.cache/upstream/gbrain';bun=ROOT/'.cache/gbrain-runtime/node_modules/@oven/bun-linux-x64/bin/bun'
    if subprocess.check_output(['git','rev-parse','HEAD'],cwd=upstream,text=True).strip()!=PIN:raise ValueError('wrong upstream pin')
    if subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=upstream,text=True).strip():raise ValueError('modified upstream')
    entries=json.loads((a.data/'index.json').read_text())['cases'];cases=[json.loads((a.data/e['path']).read_text()) for e in entries]
    texts=sorted({event_text(e) for c in cases for e in visible(c['events'],c['query'])}|{query_text(c['query']) for c in cases})
    a.cache.parent.mkdir(parents=True,exist_ok=True);db=sqlite3.connect(a.cache)
    db.execute('CREATE TABLE IF NOT EXISTS embeddings(text TEXT PRIMARY KEY,vector BLOB,origin TEXT)')
    rows=dict((t,(v,o)) for t,v,o in db.execute('SELECT text,vector,origin FROM embeddings'));missing=[t for t in texts if t not in rows]
    reserved=sum(len(t.encode())+256 for t in missing)*.02/1e6
    if reserved>5:raise ValueError('researcher embedding guard $5 exceeded')
    manifest={'status':'preparing','created_at':now(),'data_index_sha256':sha((a.data/'index.json').read_bytes()),'upstream_pin':PIN,
              'embedding_model':'text-embedding-3-small','dimensions':1024,'embedding_price_per_million':.02,'price_source':'https://developers.openai.com/api/docs/models/text-embedding-3-small.md',
              'embedding_reserved_usd':reserved,'operational_guard_usd':5,'user_numeric_budget':None,'cases':len(cases),
              'source_sha256':{str(f.relative_to(ROOT)):sha(f.read_bytes()) for f in [Path(__file__).resolve(),ROOT/'benchmarks/challenge/core.py',ROOT/'benchmarks/challenge/retrieve.py',ROOT/'benchmarks/integrated/gbrain-search.ts']}}
    if a.resume:
        old=json.loads((a.output/'manifest.json').read_text())
        for k in ['data_index_sha256','upstream_pin','source_sha256']:
            if old[k]!=manifest[k]:raise ValueError('resume changed '+k)
    dump(a.output/'manifest.json',manifest)
    if missing and not a.execute_embeddings:raise ValueError('real embedding execution flag required')
    # Unique attempt folders survive transport errors; no automatic retries.
    batches=[missing[i:i+96] for i in range(0,len(missing),96)]
    existing=len(list(a.output.glob('embedding-*')))
    def embed(item):
        i,batch=item;folder=a.output/f'embedding-{existing+i:05d}';folder.mkdir();started=now();start=time.perf_counter()
        body={'model':'text-embedding-3-small','input':batch,'dimensions':1024,'encoding_format':'base64'}
        dump(folder/'request.json',body)
        try:
            req=urllib.request.Request('https://api.openai.com/v1/embeddings',data=canonical(body).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+os.environ['RESEARCH_OPENAI_API_KEY']})
            with urllib.request.urlopen(req,timeout=120) as r:raw=r.read()
            zipped(folder/'response.json.gz',raw);result=json.loads(raw)
            if len(result['data'])!=len(batch):raise ValueError('embedding count mismatch')
            updates=[]
            for x in result['data']:
                value=x['embedding'];blob=base64.b64decode(value) if isinstance(value,str) else struct.pack('<1024f',*value)
                if len(blob)!=4096:raise ValueError('wrong embedding dimensions')
                updates.append((batch[x['index']],blob,str((folder/'response.json.gz').resolve().relative_to(ROOT))))
            dump(folder/'receipt.json',{'status':'completed','started_at':started,'seconds':time.perf_counter()-start,'model':result['model'],'usage':result['usage'],'estimated_usd':result['usage']['total_tokens']*.02/1e6})
            return updates
        except Exception as e:
            dump(folder/'receipt.json',{'status':'failed','started_at':started,'seconds':time.perf_counter()-start,'error_type':type(e).__name__,'http_status':getattr(e,'code',None)});raise
    with ThreadPoolExecutor(max_workers=4) as pool:
        for future in as_completed([pool.submit(embed,x) for x in enumerate(batches)]):
            for t,v,o in future.result():rows[t]=(v,o);db.execute('INSERT INTO embeddings VALUES (?,?,?)',(t,v,o))
            db.commit()
    vectors={}
    for t in texts:
        v=struct.unpack('<1024f',rows[t][0]);norm=math.sqrt(sum(x*x for x in v))
        if not math.isfinite(norm) or norm<=0:raise ValueError('invalid embedding')
        vectors[t]=[x/norm for x in v]
    # One compact snapshot (float32 bytes) permits replay without private cache.
    snapshot=[{'text':t,'vector_base64':base64.b64encode(rows[t][0]).decode(),'origin':rows[t][1]} for t in texts]
    zipped(a.output/'embedding-snapshot.json.gz',canonical(snapshot).encode());db.close()
    def one(case):
        folder=a.output/case['id']
        if a.resume and (folder/'receipt.json').exists():return json.loads((folder/'receipt.json').read_text())
        folder.mkdir(exist_ok=a.resume);q=case['query'];events=visible(case['events'],q);qt=query_text(q)
        inp={'query':{'id':case['id'],'text':qt,'embedding':vectors[qt]},'events':[{'id':e['id'],'text':event_text(e),'embedding':vectors[event_text(e)]} for e in events]}
        env=dict(os.environ,RESEARCH_GBRAIN_SOURCE=str(upstream),GBRAIN_HOME=str(folder.resolve()/'gbrain-home'))
        for k in ['RESEARCH_OPENAI_API_KEY','RESEARCH_ANTHROPIC_API_KEY','OPENAI_API_KEY','ANTHROPIC_API_KEY']:env.pop(k,None)
        started=time.perf_counter();proc=subprocess.run([str(bun),str(ROOT/'benchmarks/integrated/gbrain-search.ts')],input=canonical(inp),text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,timeout=300)
        (folder/'native.stdout.json').write_text(proc.stdout);(folder/'native.stderr.log').write_text(proc.stderr)
        if proc.returncode:raise ValueError('native search failure: '+case['id'])
        native=json.loads(proc.stdout)
        if not native['semantic_embedding_used'] or not native['metadata']['vector_enabled']:raise ValueError('hybrid did not execute')
        gb=[x['id'] for x in native['rankings']];bm=rank_hybrid(events,qt,{e['id']:vectors[event_text(e)] for e in events},vectors[qt])
        if len(gb)!=len(set(gb)) or not set(gb)<={e['id'] for e in events}:raise ValueError('invalid native ranking')
        packets=[]
        for arm in ARMS:
            selected=select(events,q,bm if arm=='markdown' else gb,arm,case['budget_bytes'])
            evidence_bytes=len(canonical([source_view(e) for e in selected]).encode())
            if arm!='full' and evidence_bytes>case['budget_bytes']:raise ValueError('evidence cap exceeded')
            packets.append({'arm':arm,'case_id':case['id'],'world':case['world'],'budget_bytes':case['budget_bytes'],
                            'evidence_ids':[e['id'] for e in selected],'evidence_bytes':evidence_bytes,'messages':messages(q,selected)})
        (folder/'packets.json').write_text(canonical(packets)+'\n')
        # Original lossless entity-wiki export, not an official Karpathy system.
        (folder/'company-wiki.md').write_text('# Current company records\n\n'+'\n'.join('## '+e['entity']+' / '+e['relation']+'\n\n'+canonical(source_view(e))+'\n' for e in sorted(events,key=lambda e:(e['entity'],e['relation'],e['id']))))
        receipt={'case_id':case['id'],'status':'completed','seconds':time.perf_counter()-started,'native_input_sha256':sha(canonical(inp).encode()),'visible_ids':[e['id'] for e in events],'gbrain_ranking':gb,'markdown_ranking':bm,'packets_sha256':sha((folder/'packets.json').read_bytes())}
        dump(folder/'receipt.json',receipt);return receipt
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        for row in pool.map(one,cases):print(canonical({'case':row['case_id'],'seconds':round(row['seconds'],2)}),flush=True)
    manifest.update(status='completed',finished_at=now(),embedding_snapshot_sha256=sha((a.output/'embedding-snapshot.json.gz').read_bytes()));dump(a.output/'manifest.json',manifest)

if __name__=='__main__':main()
