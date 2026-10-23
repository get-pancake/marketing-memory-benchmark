#!/usr/bin/env python3
"""Compile the manuscript with system TeX and BibTeX; no model/network calls."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=ROOT/'paper/report.pdf')
    a=p.parse_args()
    build=ROOT/'.cache/paper-build';build.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,BIBINPUTS=str(ROOT/'paper')+':')
    commands=[]
    for i,program in enumerate(['pdflatex','bibtex','pdflatex','pdflatex']):
        cmd=[program,'main'] if program=='bibtex' else [program,'-interaction=nonstopmode','-halt-on-error','-output-directory='+str(build),'main.tex']
        cwd=build if program=='bibtex' else ROOT/'paper'
        result=subprocess.run(cmd,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        (build/f'pass-{i}.log').write_text(result.stdout)
        commands.append(dict(program=program,exit_code=result.returncode))
        if result.returncode:raise SystemExit('TeX build failed; inspect '+str(build/f'pass-{i}.log'))
    log=(build/'main.log').read_text()
    if 'undefined citations' in log or 'undefined references' in log:raise SystemExit('Unresolved bibliography/references')
    a.output.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(build/'main.pdf',a.output)
    receipt=dict(created_at=datetime.now(timezone.utc).isoformat(),commands=commands,
        pdflatex=subprocess.check_output(['pdflatex','--version'],text=True).splitlines()[0],
        sources={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((ROOT/'paper').glob('*')) if f.suffix in ['.tex','.bib']},
        figures={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((ROOT/'paper/figures').rglob('*')) if f.is_file()},
        pdf_sha256=hashlib.sha256(a.output.read_bytes()).hexdigest(),
        note='Successful compilation is not visual inspection, scientific validation or publication.')
    (a.output.parent/(a.output.stem+'-build.json')).write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(output=str(a.output),sha256=receipt['pdf_sha256'])))


if __name__=='__main__':main()
