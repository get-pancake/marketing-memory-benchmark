"""Verify saved provider requests, terminal ledger, response identity and code freeze."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from benchmarks.challenge.core import canonical,sha,dump
from benchmarks.challenge.run import body

ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser()
    for n in ['data','packets','run','freeze','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();freeze=json.loads(a.freeze.read_text());manifest=json.loads((a.run/'manifest.json').read_text())
    for path,digest in freeze['code_sha256'].items():
        if sha((ROOT/path).read_bytes())!=digest:raise ValueError('frozen code changed: '+path)
    index=json.loads((a.data/'index.json').read_text());cases={e['id']:json.loads((a.data/e['path']).read_text()) for e in index['cases']}
    if sha((a.data/'index.json').read_bytes())!=freeze['data_index_sha256']:raise ValueError('frozen index changed')
    if sha((a.packets/'manifest.json').read_bytes())!=freeze['packets_manifest_sha256']:raise ValueError('preparation manifest changed')
    providers={x['provider']:x for x in manifest['config']['providers']};ledger=[json.loads(s) for s in (a.run/'attempts.jsonl').read_text().splitlines()]
    issued=[r['id'] for r in ledger if r['status']=='issued'];terminal=[r for r in ledger if r['status'] in ['completed','failed','interrupted']]
    if len(issued)!=len(set(issued)) or len(terminal)!=len({r['id'] for r in terminal}):raise ValueError('duplicate issued or terminal entry')
    planned={r['id'] for r in manifest['planned']}
    if set(issued)!=planned or {r['id'] for r in terminal}!=planned:raise ValueError('unattempted/incomplete manifest')
    response_ids=[];models={};requests=0;raw_responses=0
    for plan in manifest['planned']:
        case=cases[plan['case_id']];packet=next(x for x in json.loads((a.packets/case['id']/'packets.json').read_text()) if x['arm']==plan['arm'])
        expected=body(providers[plan['provider']],packet,case['query'],manifest['config']['max_output_tokens']);folder=a.run/plan['id']
        if json.loads((folder/'request.json').read_text())!=expected:raise ValueError('request differs from declared intervention')
        requests+=1
        if (folder/'response.json').exists():
            raw=json.loads((folder/'response.json').read_text());response_ids.append(raw['id']);models[raw['model']]=models.get(raw['model'],0)+1;raw_responses+=1
            if raw['model']!=providers[plan['provider']]['model']:raise ValueError('returned model differs from frozen requested ID')
    if len(response_ids)!=len(set(response_ids)):raise ValueError('duplicate response ID')
    dump(a.output,{'status':'passed','requests_reconstructed':requests,'raw_responses':raw_responses,'distinct_response_ids':len(set(response_ids)),
                   'terminal_attempts':len(terminal),'models':models,'code_hashes_verified':len(freeze['code_sha256']),
                   'frozen_revision':freeze['code_revision'],'fresh_api_calls':0,'scope':'Request equality, distinct responses, complete all-attempt ledger and frozen inputs/code; semantic scores independently rebuilt by analyze.py.'})
    print(canonical({'status':'passed','requests':requests,'models':models}))

if __name__=='__main__':main()
