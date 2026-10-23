#!/usr/bin/env python3
"""Generate the complete context-budget table from the saved component analyses."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
METHODS=[('generic_hybrid','Generic hybrid'),('prompt_hybrid','Prompt hybrid'),
         ('facet_hybrid','Generic relation diversity'),('gbrain_hybrid','GBrain hybrid component'),
         ('typed','Catalog coverage'),('gbrain_catalog_coverage','GBrain + catalog coverage')]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--analysis-root',type=Path,default=ROOT/'analysis/gbrain')
    p.add_argument('--output',type=Path,default=ROOT/'paper/figures/context-budget-table.tex')
    a=p.parse_args();data={};sources={}
    for cap in [1024,1536,4096]:
        path=a.analysis_root/f'reproducible-{cap}/summary.json';raw=path.read_bytes()
        data[cap]=json.loads(raw);sources[str(cap)]=hashlib.sha256(raw).hexdigest()
    lines=[r'\begin{tabular}{lrrr}',r'\toprule',
           r'Method & 1,024 tokens & 1,536 tokens & 4,096 tokens \\',r'\midrule']
    for name,label in METHODS:
        values=[]
        for cap in data:
            x=data[cap]['methods'][name]
            values.append(f"{x['complete_positive_support']}/{x['positive_cases']}")
        lines.append(label+' & '+' & '.join(values)+r' \\')
    lines.extend([r'\bottomrule',r'\end{tabular}'])
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text('\n'.join(lines)+'\n')
    a.output.with_suffix('.json').write_text(json.dumps(dict(source_summary_sha256=sources,
        table_sha256=hashlib.sha256(a.output.read_bytes()).hexdigest(),
        metric='Complete acceptable current evidence set on answerable cases; no recommendation claim.'),indent=2)+'\n')
    print(json.dumps({'output':str(a.output),'source_hashes':sources}))

if __name__=='__main__':main()
