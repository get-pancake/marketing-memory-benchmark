"""Describe actual native search execution without turning it into a product rank."""
import argparse,json,sys
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from benchmarks.challenge.core import dump,canonical

def main():
    p=argparse.ArgumentParser();p.add_argument('--packets',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();rows=[]
    for path in sorted(a.packets.glob('*/native.stdout.json')):
        result=json.loads(path.read_text());m=result['metadata']
        rows.append({'case_id':path.parent.name,'retrieved':m['retrieved_count'],'keyword_top_score':m.get('keyword_arm_confidence',{}).get('top_score'),
                     'vector_enabled':m['vector_enabled'],'metadata_boost_reason':m.get('metadata_boost_gate',{}).get('reason')})
    summary={'cases':len(rows),'vector_enabled':sum(r['vector_enabled'] for r in rows),'keyword_nonzero_cases':sum((r['keyword_top_score'] or 0)>0 for r in rows),
             'retrieved_counts':dict(sorted(Counter(r['retrieved'] for r in rows).items())),
             'scope':'Native hybrid entry point ran with shared long composite queries; lexical arm had no matching full query. This is configured component telemetry, not evidence that the complete GBrain agent cannot retrieve these facts. All closure methods receive the same ranking; generic query-word closure is a stronger matched-input control.',
             'rows':rows}
    dump(a.output,summary);print(canonical({k:v for k,v in summary.items() if k not in ['rows','scope']}))

if __name__=='__main__':main()
