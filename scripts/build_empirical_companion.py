#!/usr/bin/env python3
"""Prepare a strictly allowlisted empirical companion ZIP; never publish it."""
import argparse
import gzip
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FIXED = [
    'release/README.md', 'release/LICENSE-CODE', 'release/LICENSE-DATA', 'release/GITIGNORE',
    'release/REPRODUCING.md', 'release/CITATION.cff', 'release/CONTRIBUTING.md',
    'release/github-actions.yml', 'release/RELEASE_NOTES.md',
    'release/THIRD_PARTY.md', 'release/SEARCH_METHODOLOGY.md', 'release/TUNING.md',
    'release/SCORING_AUDIT.md',
    'release/PUBLICATION_STATUS.md',
    'release/VISUAL_INSPECTION.json',
    'release/requirements-analysis.in', 'release/requirements-analysis.lock',
    'release/literature-index.json', 'release/CLAIMS.json',
    'release/literature-integrated-index.json',
    'sources/bibliography-audit.json', 'sources/verified-venue-metadata.json',
    'literature/SEARCH_LOG.md', 'literature/COMPARISON.md', 'literature/GAP_AND_REUSE.md',
    'literature/artifacts.json',
    'literature/retrievals.jsonl', 'literature/diagnostics/enterprisemem-scorer.json',
    'papers/company-memory/protocol/main-v1.md',
    'papers/company-memory/protocol/pilot-v1.md',
    'papers/company-memory/protocol/main-planning-rule.md',
    'papers/company-memory/protocol/amendments.md',
    'experiments/freeze-1024.json', 'experiments/freeze-1536.json',
    'experiments/qwen3-moe-study.json', 'experiments/qwen3-moe-runtime.json',
    'experiments/runtime-environment.json',
    'experiments/qwen3-4b-local.json', 'experiments/qwen3-4b-study.json',
    'experiments/qwen3-4b-study-structured.json',
    'experiments/qwen3.5-9b-study.json', 'experiments/qwen3.5-9b-runtime.json',
    'experiments/qwen3.5-9b-avx512-study.json', 'experiments/qwen3.5-9b-avx512-runtime.json',
    'data/public/DATA_CARD.md', 'data/study/DATA_CARD.md',
    'worklog/avx512-build.md', 'worklog/qwen35-token-budget-audit.json',
    'scripts/setup_local_inference.sh', 'scripts/start_research_model.sh',
    'scripts/download_research_model.py', 'scripts/run_frozen_study.py',
    'scripts/compile_paper.py', 'scripts/compile_investor_note.py',
    'scripts/verify_report_claims.py',
    'scripts/audit_enterprisemem_scorer.py', 'scripts/research_sources.py',
    'scripts/reproduce_saved.py', 'scripts/finalize_evidence.py',
    'scripts/build_empirical_companion.py',
    'scripts/shard_embedding_snapshot.py',
    'analysis/challenge_audit.py', 'analysis/challenge_trace_audit.py',
    'analysis/challenge_budget.py', 'analysis/challenge_figures.py',
    'analysis/challenge_accounting.py', 'scripts/register_challenge_claims.py',
    'analysis/challenge_external_opus.py', 'scripts/hydrate_challenge_cache.py',
    'analysis/challenge_native_telemetry.py',
    'analysis/challenge_diagnostics.py', 'scripts/replay_challenge_native.py',
    'papers/company-memory/protocol/challenge-external-opus.md',
    'data/challenge/DATA_CARD.md', 'literature/challenge-fetch.json',
    'papers/company-memory/protocol/challenge-v1.md',
    'papers/company-memory/protocol/challenge-amendment-01.md',
    'papers/company-memory/protocol/challenge-amendment-02.md',
    'scripts/fetch_external_company_data.py',
    'analysis/separate_context.py',
    'analysis/analyze_study.py', 'analysis/audit_run.py', 'analysis/figures.py',
    'analysis/test_analysis.py', 'analysis/main/evidence-build.json',
    'analysis/test_audit.py',
    'analysis/error_localization.py',
    'analysis/main/primary/error-localization.json',
    'analysis/main/sensitivity/error-localization.json',
    'analysis/input_capacity.py', 'analysis/diagnostics/input-capacity.json',
    'analysis/diagnostics/input-budget.json',
    'analysis/output_capacity.py', 'analysis/diagnostics/output-capacity.json',
    'analysis/cost_accounting.py', 'analysis/main/cost-accounting.json',
    'paper/report.pdf', 'paper/report-build.json', 'paper/investor-note.md',
    'paper/investor-note.pdf', 'paper/investor-note-build.json',
    'paper/abstract.tex', 'paper/results.tex', 'paper/discussion.tex',
]
PILOTS = ['compact-contract-a', 'compact-contract-a2', 'compact-contract-a3',
          'qwen35-competence', 'qwen35-bound-citations', 'qwen3-moe-competence',
          'qwen3-moe-support-table', 'qwen3-moe-alternatives', 'stage-b',
          'cache-smoke', 'sql-reference']
DATA = ['pilot-v1', 'pilot-v2', 'pilot-v3', 'pilot-v4', 'pilot-v5',
        'runtime-smoke-v1', 'main-v1']
PRIVATE = re.compile(r'github\.com/get-pancake/pancake-cmo|/Us' r'ers/|'
                     r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|'
                     r'\bsk-(?:proj-|ant-api\d+-)?[A-Za-z0-9_-]{20,}')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def payload_digest(payloads):
    rows = [{'path': p, 'sha256': sha(b)} for p, b in sorted(payloads.items())
            if not p.startswith('release/reproduction-records/')
            and p != 'release/ACCEPTANCE.md']
    return sha(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode())


def files_below(folder, suffixes):
    root = ROOT / folder
    if not root.is_dir():
        raise ValueError('Missing allowlisted directory: ' + folder)
    selected = []
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        if any(part.startswith('.') or part == '__pycache__' for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError('Symlink in allowlisted directory: ' + str(path))
        if path.is_file():
            if folder.startswith('experiments/challenge'):
                if path.name == 'embedding-snapshot.json.gz':
                    continue  # losslessly sharded next to the original
                if 'provider-access-v1' in relative.parts and path.name not in {'access.json', 'pricing-evidence.json'}:
                    continue  # no copied third-party HTML or entire model catalog
            if path.suffix not in suffixes:
                raise ValueError('Unexpected file in allowlisted directory: ' + str(path))
            selected.append(str(path.relative_to(ROOT)))
    if not selected:
        raise ValueError('Empty allowlisted directory: ' + folder)
    return selected


def select_files():
    names = list(FIXED)
    for folder in ['prototype', 'study', 'tests']:
        names += files_below(folder, {'.py', '.md'})
    for folder, suffixes in [
        ('benchmarks', {'.py', '.ts', '.md', '.json'}),
        ('analysis/context-v1', {'.json', '.jsonl'}),
        ('analysis/gbrain', {'.json', '.jsonl'}),
        ('experiments/gbrain', {'.json', '.jsonl', '.py', '.ts', '.md', '.log'}),
        ('experiments/recommendation', {'.json'}),
        ('papers/marketing-memory', {'.md'}),
        ('papers/marketing-recommendation', {'.md'}),
        ('data/external/messy-company-v1', {'.md', '.json', '.jsonl', ''}),
        ('release/history/v1', {'.pdf', '.md', '.json'}),
        ('release/history/v2', {'.pdf', '.md', '.json'}),
        ('release/history/v3', {'.pdf', '.md', '.json', '.tex'}),
        ('data/challenge', {'.json', '.md'}),
        ('experiments/challenge', {'.json', '.jsonl', '.py', '.ts', '.md', '.log', '.gz'}),
        ('analysis/challenge', {'.json', '.csv'}),
        ('data/integrated', {'.json', '.md'}),
        ('experiments/integrated', {'.json', '.jsonl', '.py', '.ts', '.md', '.log'}),
        ('experiments/provider-access-2026-10-22', {'.json', '.jsonl', '.py', '.md', '.log'}),
        ('analysis/integrated', {'.json', '.jsonl'}),
    ]:
        names += files_below(folder, suffixes)
    names += files_below('literature/reviews', {'.md'})
    names += files_below('data/public/dev', {'.json'})
    for version in DATA:
        names += files_below('data/study/' + version, {'.json'})
    for run in PILOTS:
        names += files_below('experiments/pilot/' + run, {'.json', '.jsonl', '.py'})
    for run in ['2026-10-21-contract-v0.1', '2026-10-22-inference-calibration']:
        names += files_below('experiments/development/' + run, {'.json', '.jsonl'})
    for block in ['primary', 'sensitivity']:
        names += files_below('experiments/main/' + block, {'.json', '.jsonl', '.py'})
        names += files_below('analysis/main/' + block, {'.json', '.jsonl'})
    names += files_below('experiments/main/sql-reference', {'.json', '.jsonl'})
    names += files_below('analysis/pilot', {'.json', '.jsonl'})
    names += [str(p.relative_to(ROOT)) for p in (ROOT / 'analysis/main').glob('*.log')]
    names += [str(p.relative_to(ROOT)) for p in (ROOT / 'paper').glob('*')
              if p.suffix in {'.tex', '.bib'}]
    names += files_below('paper/figures', {'.pdf', '.svg', '.tex', '.json'})
    return sorted(set(names))


def read_public(name):
    path = ROOT / name
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(ROOT):
        raise ValueError('Unsafe or missing allowlisted file: ' + name)
    data = path.read_bytes()
    text_data = gzip.decompress(data) if path.suffix == '.gz' else data
    if path.suffix != '.pdf' and PRIVATE.search(text_data.decode('utf-8')):
        raise ValueError('Private pointer or credential-like content: ' + name)
    return data


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--candidate', action='store_true',
                   help='Permit packaging before clean reproduction; still requires complete main evidence.')
    a = p.parse_args()
    challenge = json.loads((ROOT / 'analysis/challenge/main-v1/summary.json').read_text())
    challenge_audit = json.loads((ROOT / 'analysis/challenge/main-trace-audit.json').read_text())
    challenge_context = json.loads((ROOT / 'analysis/challenge/main-context-audit.json').read_text())
    if (challenge['worlds'] != 120 or challenge['attempts'] != 4320
            or challenge_audit['status'] != 'passed' or challenge_audit['terminal_attempts'] != 4320
            or challenge_context['query_word_exact_equal_cases'] != 360):
        raise ValueError('Frozen challenge evidence, all-attempt trace audit or strong-control audit incomplete')
    integrated = json.loads((ROOT / 'analysis/integrated/main-v1/summary.json').read_text())
    integrated_audit = json.loads((ROOT / 'analysis/integrated/main-audit-v1/audit.json').read_text())
    external = json.loads((ROOT / 'analysis/integrated/external-v1/summary.json').read_text())
    if integrated['run_status'] != 'completed' or integrated['planned_calls'] != 3696 or not integrated_audit['passed']:
        raise ValueError('Integrated main evidence or audit is incomplete')
    if external['planned_calls'] != 220 or external['attempted'] != 220 or external['run_status'] != 'completed':
        raise ValueError('External wiki attempts incomplete; failed attempts must remain in the analysis')
    chunks = json.loads((ROOT / 'analysis/integrated/external-chunks-v1/summary.json').read_text())
    if chunks['run_status'] != 'completed' or chunks['planned_calls'] != 44 or sum(g['cases'] for g in chunks['groups'].values()) != 44:
        raise ValueError('Disclosed post-hoc external chunk control is incomplete')
    evidence = json.loads((ROOT / 'analysis/main/evidence-build.json').read_text())
    if not evidence['complete']:
        raise ValueError('Evidence build is incomplete')
    for block, planned in [('primary', 576), ('sensitivity', 192)]:
        run = json.loads((ROOT / 'experiments/main' / block / 'manifest.json').read_text())
        if not run['complete']:
            raise ValueError('Incomplete main block: ' + block)
        audit = json.loads((ROOT / 'analysis/main' / block / 'provenance-audit.json').read_text())
        summary = json.loads((ROOT / 'analysis/main' / block / 'summary.json').read_text())
        if not run['complete'] or not audit['passed'] or audit['planned'] != planned:
            raise ValueError('Incomplete or unaudited main block: ' + block)
        if not summary['source_run_complete'] or summary['planned_attempts'] != planned:
            raise ValueError('Incomplete main analysis: ' + block)
    report = json.loads((ROOT / 'paper/report-build.json').read_text())
    note = json.loads((ROOT / 'paper/investor-note-build.json').read_text())
    visual = json.loads((ROOT / 'release/VISUAL_INSPECTION.json').read_text())
    if not visual.get('passed'):
        raise ValueError('Final PDF visual inspection is pending')
    for name, receipt in [('report', report), ('investor-note', note)]:
        pdf = ROOT / 'paper' / (name + '.pdf')
        digest = sha(pdf.read_bytes())
        if receipt['pdf_sha256'] != digest:
            raise ValueError('PDF differs from its build receipt: ' + name)
        checked = visual['documents'].get('paper/' + name + '.pdf', {})
        pages = checked.get('pages', 0)
        if (checked.get('pdf_sha256') != digest or pages < 1
                or checked.get('checked_pages') != list(range(1, pages + 1))):
            raise ValueError('Visual inspection does not cover this exact PDF: ' + name)
    if not report.get('figures'):
        raise ValueError('Paper build receipt has no final figure hashes')
    for kind in ['sources', 'figures']:
        for path, digest in report[kind].items():
            if sha((ROOT / path).read_bytes()) != digest:
                raise ValueError('Paper input changed after compilation: ' + path)
    if (sha((ROOT / note['source']).read_bytes()) != note['source_sha256']
            or sha((ROOT / 'paper/investor-note.tex').read_bytes()) != note['generated_tex_sha256']
            or note['pages'] != 2):
        raise ValueError('Investor-note sources changed or length differs')
    payloads = {name: read_public(name) for name in select_files()}
    payloads['README.md'] = payloads['release/README.md']
    payloads['LICENSE'] = payloads['release/LICENSE-CODE']
    payloads['LICENSE-DATA'] = payloads['release/LICENSE-DATA']
    payloads['.gitignore'] = payloads['release/GITIGNORE']
    payloads['CITATION.cff'] = payloads['release/CITATION.cff']
    payloads['CONTRIBUTING.md'] = payloads['release/CONTRIBUTING.md']
    payloads['.github/workflows/checks.yml'] = payloads['release/github-actions.yml']
    digest = payload_digest(payloads)
    verified = False
    evidence_dir = ROOT / 'release/reproduction-records'
    if evidence_dir.is_dir():
        for name in files_below('release/reproduction-records', {'.json', '.jsonl', '.log', '.txt', '.py'}):
            payloads[name] = read_public(name)
        receipt_path = evidence_dir / 'clean-reproduction.json'
        if receipt_path.exists():
            receipt = json.loads(receipt_path.read_text())
            verified = receipt.get('passed', False) and receipt.get('core_payload_sha256') == digest
    if not a.candidate and not verified:
        raise ValueError('No passing clean-reproduction receipt for this exact payload; build/test a candidate first.')
    if (ROOT / 'release/ACCEPTANCE.md').exists():
        payloads['release/ACCEPTANCE.md'] = read_public('release/ACCEPTANCE.md')
    commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True, capture_output=True)
    manifest = {
        'schema': 'marketing-memory-opus-challenge-companion-v4',
        'release_version': '1.0.0',
        'intended_public_repository': 'https://github.com/get-pancake/marketing-memory-benchmark',
        'kind': 'empirical_release_candidate' if a.candidate else 'tested_empirical_companion',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'working_revision': commit.stdout.strip() if commit.returncode == 0 else None,
        'frozen_experiment_revision': challenge_audit['frozen_revision'],
        'prior_integrated_experiment_revision': '61c57c67c1bb4d356ce5ea38672c522df6958138',
        'core_payload_sha256': digest,
        'clean_reproduction_verified': verified,
        'published': False, 'paper_submitted': False,
        'publication_note': 'Publication is not observed by this packaging command; verify live hosting separately.',
        'scope': 'Opus/GPT controlled multi-account context and decision challenge, plus retained prior integrated and exploratory external-company wiki evidence. No commercial or human validation.',
        'broader_research_program_complete': False,
        'frontier_provider_comparison_complete': True,
        'reproduction_scope': 'All hashed payload files except reproduction records and acceptance narrative; fresh full benchmark rerun is a separate operation.',
        'files': [{'path': name, 'bytes': len(data), 'sha256': sha(data)}
                  for name, data in sorted(payloads.items())],
    }
    payloads['MANIFEST.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(a.output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(payloads.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 22, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    print(json.dumps({'archive': str(a.output), 'files': len(payloads),
                      'sha256': sha(a.output.read_bytes()), 'core_payload_sha256': digest,
                      'clean_reproduction_verified': verified, 'published': False}))


if __name__ == '__main__':
    main()
