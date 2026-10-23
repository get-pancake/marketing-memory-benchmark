"""Attach final numerical evidence to the existing immutable historical register."""
import json,hashlib,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def walk(value,keys=()):
    if type(value) in (int,float) or isinstance(value,str) and re.fullmatch(r'-?\d+\.\d+',value):yield list(keys),value
    elif isinstance(value,dict):
        for k,v in value.items():yield from walk(v,keys+(k,))
    elif isinstance(value,list):
        for i,v in enumerate(value):yield from walk(v,keys+(i,))
def main():
    path=ROOT/'release/CLAIMS.json';register=json.loads(path.read_text());register['claims']=[c for c in register['claims'] if not c['id'].startswith('C4-')]
    sources=[('analysis/challenge/main-v1/summary.json','Frozen main paired outcomes and uncertainty.'),
             ('analysis/challenge/main-context-audit.json','Source provenance, exact generic-control equivalence and corpus sizes.'),
             ('analysis/challenge/main-trace-audit.json','Actual requests, response IDs, model identifiers and frozen code.'),
             ('analysis/challenge/main-oracle.json','Independent SQLite/exhaustive reference agreement.'),
             ('analysis/challenge/main-budget.json','Descriptive context sensitivity; no extra reader calls.'),
             ('analysis/challenge/accounting.json','Physical response counts and token-usage cost estimates.'),
             ('analysis/challenge/pilot-v1/summary.json','Initial development pilot and prospective precision rule.'),
             ('analysis/challenge/conflict-validation.json','Targeted pre-main prompt validation.'),
             ('analysis/challenge/external-opus/summary.json','Actual Opus replay of fixed external development contexts; not new independent test data.'),
             ('analysis/challenge/native-telemetry.json','Native component configuration and voting telemetry; not a whole-product ranking.'),
             ('analysis/challenge/diagnostics.json','Post-hoc descriptive citation and decision diagnostics; primary analysis unchanged.'),
             ('analysis/challenge/native-replay.json','Actual three-case native replay from public cached embeddings; no provider calls.'),
             ('paper/figures/challenge/metrics.json','Numerical values used in final figures/tables.')]
    for i,(name,statement) in enumerate(sources):
        raw=(ROOT/name).read_bytes();obj=json.loads(raw)
        # Per-case rows remain inspectable but do not need thousands of duplicate
        # register entries when aggregate claims are explicitly keyed.
        excluded={'rows','records','selected_examples','all_reader_shortfalls'};selected={k:v for k,v in obj.items() if k not in excluded}
        quantities=[{'name':'.'.join(map(str,keys)),'value':value,'sources':[{'artifact':name,'sha256':hashlib.sha256(raw).hexdigest(),'keys':keys}]} for keys,value in walk(selected)]
        register['claims'].append({'id':'C4-'+str(i+1),'statement':statement,'quantities':quantities,'report_scope':'Opus challenge v4'})
    register.update(as_of='2026-10-23',scope='Retained historical evidence plus the current Opus/GPT challenge; register checks are not prose or scientific peer review.',reproduction_status='New v4 candidate must pass clean reproduction before final packaging.')
    path.write_text(json.dumps(register,indent=2)+'\n');print(json.dumps({'new_claim_groups':len(sources),'numeric_quantities':sum(len(c.get('quantities',[])) for c in register['claims'])}))
if __name__=='__main__':main()
