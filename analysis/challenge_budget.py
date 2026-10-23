"""Descriptive retrieval-only budget sweep; never invokes a reader/provider."""
import argparse,json,sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from benchmarks.challenge.core import dump,visible,score,canonical
from benchmarks.challenge.retrieve import select

BUDGETS=[4096,8192,16384,32768,65536,131072]
ARMS=['company','gtm','markdown','gbrain']
def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--packets',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    rows=[]
    for entry in json.loads((a.data/'index.json').read_text())['cases']:
        case=json.loads((a.data/entry['path']).read_text());ev=visible(case['events'],case['query']);rec=json.loads((a.packets/case['id']/'receipt.json').read_text())
        for cap in BUDGETS:
            for arm in ARMS:
                selected=select(ev,case['query'],rec['markdown_ranking'] if arm=='markdown' else rec['gbrain_ranking'],arm,cap)
                value=score({'actions':[]},case,selected)
                rows.append({'case_id':case['id'],'world':case['world'],'level':case['level'],'arm':arm,'budget_bytes':cap,'normalized_recoverable_value':value['context_normalized_value']})
    summary=[]
    for cap in BUDGETS:
        for arm in ARMS:
            by=defaultdict(list)
            for r in rows:
                if r['budget_bytes']==cap and r['arm']==arm and r['normalized_recoverable_value'] is not None:by[r['world']].append(r['normalized_recoverable_value'])
            summary.append({'arm':arm,'budget_bytes':cap,'worlds':len(by),'mean_normalized_recoverable_value':sum(sum(v)/len(v) for v in by.values())/len(by)})
    dump(a.output,{'scope':'descriptive retrieval-only sweep; zero additional reader/embedding calls; not reader performance at alternative budgets','budgets':BUDGETS,'summary':summary,'rows':rows,'fresh_api_calls':0})
    print(canonical({'cases':len(rows)//len(BUDGETS)//len(ARMS),'context_evaluations':len(rows),'fresh_api_calls':0}))

if __name__=='__main__':main()
