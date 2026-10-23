#!/usr/bin/env python3
"""Render the single-source investor Markdown as exactly two LaTeX/PDF pages."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=ROOT / 'paper/investor-note.pdf')
    a = p.parse_args()
    source = ROOT / 'paper/investor-note.md'
    body = source.read_text()
    if body.count('<!-- pagebreak -->') != 1:
        raise ValueError('The two-page note must contain exactly one explicit pagebreak marker.')
    build = ROOT / '.cache/investor-note-build'
    build.mkdir(parents=True, exist_ok=True)
    (build / 'note.md').write_text(body.replace('<!-- pagebreak -->', '\n\\newpage\n'))
    commands = [
        ['pandoc', 'note.md', '--from=markdown+raw_tex', '--to=latex', '--standalone',
         '--variable=fontsize:11pt', '--variable=geometry:margin=0.9in', '--output=note.tex'],
        ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'note.tex'],
        ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'note.tex'],
    ]
    receipts = []
    for i, command in enumerate(commands):
        result = subprocess.run(command, cwd=build, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True)
        log = build / f'pass-{i}.log'
        log.write_text(result.stdout)
        receipts.append(dict(argv=command, exit_code=result.returncode, log_sha256=sha(log)))
        if result.returncode:
            raise RuntimeError('Investor-note rendering failed; inspect ' + str(log))
    info = subprocess.check_output(['pdfinfo', str(build / 'note.pdf')], text=True)
    match = re.search(r'^Pages:\s+(\d+)$', info, re.MULTILINE)
    if not match or int(match.group(1)) != 2:
        raise ValueError('Investor note is not exactly two pages; edit the single Markdown source.')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(build / 'note.pdf', a.output)
    tex = a.output.with_suffix('.tex')
    shutil.copyfile(build / 'note.tex', tex)
    receipt = dict(created_at=datetime.now(timezone.utc).isoformat(), pages=2,
        source='paper/investor-note.md', source_sha256=sha(source),
        generated_tex_sha256=sha(tex), pdf_sha256=sha(a.output), commands=receipts,
        pandoc=subprocess.check_output(['pandoc', '--version'], text=True).splitlines()[0],
        pdflatex=subprocess.check_output(['pdflatex', '--version'], text=True).splitlines()[0],
        note='Single Markdown content source; successful rendering does not imply visual inspection or independent review.')
    a.output.with_name(a.output.stem + '-build.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'output': str(a.output), 'pages': 2, 'sha256': receipt['pdf_sha256']}))


if __name__ == '__main__':
    main()
