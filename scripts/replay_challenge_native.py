"""Rerun three fixed native GBrain cases from released vectors without APIs."""
import argparse,json,os,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from benchmarks.challenge.core import dump,sha
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);p.add_argument('--analyze-existing',action='store_true');a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=a.analyze_existing)
    idx=json.loads((ROOT/'data/challenge/main-v1/index.json').read_text())
    entries=sorted(idx['cases'],key=lambda e:e['id'])[:3]
    # Lexicographically first world, all three stress levels; never selected by outcome.
    reduced=dict(idx,cases=entries,worlds=1)
    for e in entries:
        data=(ROOT/'data/challenge/main-v1'/e['path']).read_bytes();dest=a.output/'data'/e['path'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    dump(a.output/'data/index.json',reduced)
    env=dict(os.environ)
    for k in ['RESEARCH_OPENAI_API_KEY','RESEARCH_ANTHROPIC_API_KEY','OPENAI_API_KEY','ANTHROPIC_API_KEY']:env.pop(k,None)
    cmds=[
      [sys.executable,'scripts/hydrate_challenge_cache.py','--snapshot','experiments/challenge/main-context-v1/embedding-snapshot.json.gz','--output',str(a.output/'cache.sqlite')],
      [sys.executable,'-m','benchmarks.challenge.prepare','--data',str(a.output/'data'),'--output',str(a.output/'contexts'),'--cache',str(a.output/'cache.sqlite'),'--workers','2']]
    for i,cmd in enumerate([] if a.analyze_existing else cmds):
        result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        (a.output/f'command-{i}.log').write_text(result.stdout)
        if result.returncode:raise RuntimeError('Native replay command failed; inspect output logs.')
    comparisons=[]
    for e in entries:
        original=ROOT/'experiments/challenge/main-context-v1'/e['id'];fresh=a.output/'contexts'/e['id']
        expected=json.loads((original/'receipt.json').read_text());actual=json.loads((fresh/'receipt.json').read_text())
        for k in ['native_input_sha256','gbrain_ranking','packets_sha256','visible_ids']:
            if expected[k]!=actual[k]:raise ValueError('Native replay differs: '+e['id']+'/'+k)
        if (original/'packets.json').read_bytes()!=(fresh/'packets.json').read_bytes():raise ValueError('Packet bytes differ')
        comparisons.append({'case_id':e['id'],'native_input_sha256':actual['native_input_sha256'],'packets_sha256':actual['packets_sha256'],'native_candidates':len(actual['gbrain_ranking']),'markdown_full_ranking_identical':actual['markdown_ranking']==expected['markdown_ranking']})
        saved=a.receipt.parent/'native-replay-records'/e['id'];saved.mkdir(parents=True,exist_ok=a.analyze_existing)
        for name in ['native.stdout.json','receipt.json']:(saved/name).write_bytes((fresh/name).read_bytes())
    if list((a.output/'contexts').glob('embedding-*/request.json')):raise ValueError('Unexpected embedding request')
    dump(a.receipt,{'status':'passed','cases':len(entries),'packets':len(entries)*6,'fresh_native_search':True,'fresh_api_calls':0,'credential_variables_removed':True,'comparison':'Exact input hashes, native GBrain ranking order and every packet byte; native timing fields may differ. The auxiliary Markdown full ranking can differ at near-ties due to unordered floating-point BM25 summation; full ranking equality is recorded separately. The frozen code is unchanged, and saved-output reproduction uses original rankings. Same host, freshly created PGLite instances, released vector snapshot.','records':comparisons})
    print(json.dumps({'status':'passed','native_cases':len(entries),'fresh_api_calls':0}))
if __name__=='__main__':main()
