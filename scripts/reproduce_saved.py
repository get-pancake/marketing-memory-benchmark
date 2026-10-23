#!/usr/bin/env python3
"""Verify an extracted companion, regenerate saved-result analysis, and compile."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build_empirical_companion import payload_digest


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_summary(path):
    result = json.loads(path.read_text())
    for key in ['analyzed_at', 'run', 'dataset']:
        result.pop(key, None)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True,
                   help='New directory for logs and regenerated evidence; never overwrite saved results.')
    p.add_argument('--fresh-smoke', action='store_true',
                   help='Also make two real reader calls against already running pinned local services.')
    p.add_argument('--upstream-scorer-check', action='store_true',
                   help='Also reproduce the literature scorer diagnostic; requires three public hash-checked GitHub files if not cached.')
    a = p.parse_args()
    output = a.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((ROOT / 'MANIFEST.json').read_text())
    manifest_sha256 = digest(ROOT / 'MANIFEST.json')
    payloads = {}
    for record in manifest['files']:
        path = ROOT / record['path']
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT) or digest(path) != record['sha256']:
            raise ValueError('Package file hash mismatch: ' + record['path'])
        payloads[record['path']] = path.read_bytes()
    core = payload_digest(payloads)
    if core != manifest['core_payload_sha256']:
        raise ValueError('Package payload hash mismatch')
    receipt = dict(started_at=datetime.now(timezone.utc).isoformat(), passed=False,
                   core_payload_sha256=core, package_files_verified=len(payloads),
                   package_manifest_sha256=manifest_sha256,
                   python=sys.version, executable=sys.executable, platform=platform.platform(),
                   independent_hardware=False, fresh_runtime_compilation=False,
                   fresh_full_main_inference=False, fresh_smoke_requested=a.fresh_smoke,
                   upstream_scorer_requested=a.upstream_scorer_check,
                   commands=[], checks={},
                   scope='Clean extracted code/data and isolated Python environment; system TeX and, if requested, existing pinned local model services remain external dependencies.')
    receipt_path = output / 'clean-reproduction.json'
    def save():
        receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
    def run(label, command):
        result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True)
        log = output / (label + '.log')
        log.write_text(result.stdout)
        receipt['commands'].append(dict(label=label, argv=command, exit_code=result.returncode,
                                         output_sha256=digest(log)))
        save()
        if result.returncode:
            raise RuntimeError('Reproduction command failed: ' + label)
        print(label + ': passed', flush=True)
    save()
    try:
        run('tests-original', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'])
        run('tests-study', [sys.executable, '-m', 'unittest', 'study.test_contract',
                           'study.test_ledger', 'analysis.test_analysis', 'analysis.test_audit', '-v'])
        generated = output / 'regenerated-data'
        run('data', [sys.executable, '-m', 'study.fixtures', '--split', 'test', '--worlds', '12',
                     '--seed', '2026102202', '--output', str(generated)])
        for name in ['inputs.json', 'labels.json']:
            if digest(generated / name) != digest(ROOT / 'data/study/main-v1' / name):
                raise ValueError('Dataset regeneration differs: ' + name)
        receipt['checks']['main_dataset_byte_identical'] = True
        run('input-capacity', [sys.executable, 'analysis/input_capacity.py',
                              '--verify-saved', 'analysis/diagnostics/input-capacity.json'])
        receipt['checks']['input_capacity_receipts_verified_offline'] = True
        run('output-capacity', [sys.executable, 'analysis/output_capacity.py',
                               '--verify-saved', 'analysis/diagnostics/output-capacity.json'])
        receipt['checks']['output_capacity_receipts_verified_offline'] = True
        for block in ['primary', 'sensitivity']:
            run_path = 'experiments/main/' + block
            dest = output / 'analysis' / block
            run('audit-' + block, [sys.executable, 'analysis/audit_run.py', '--run', run_path,
                                   '--data', 'data/study/main-v1', '--output', str(dest / 'provenance-audit.json')])
            run('analysis-' + block, [sys.executable, 'analysis/analyze_study.py', '--run', run_path,
                                      '--data', 'data/study/main-v1', '--output', str(dest)])
            expected = ROOT / 'analysis/main' / block
            if stable_summary(dest / 'summary.json') != stable_summary(expected / 'summary.json'):
                raise ValueError('Saved-result analysis differs: ' + block)
            for name in ['per-attempt.jsonl', 'provenance-audit.json']:
                if digest(dest / name) != digest(expected / name):
                    raise ValueError('Recomputed artifact differs: ' + block + '/' + name)
            receipt['checks'][block + '_analysis_identical_excluding_timestamp_and_paths'] = True
            localized = dest / 'error-localization.json'
            run('errors-' + block, [sys.executable, 'analysis/error_localization.py',
                '--analysis', str(dest), '--output', str(localized)])
            original_errors = json.loads((expected / 'error-localization.json').read_text())
            reproduced_errors = json.loads(localized.read_text())
            for item in [original_errors, reproduced_errors]:
                item.pop('created_at', None)
            if original_errors != reproduced_errors:
                raise ValueError('Error localization differs: ' + block)
            receipt['checks'][block + '_error_localization_identical_excluding_timestamp'] = True
            figures = output / 'figures' / block
            run('figures-' + block, [sys.executable, 'analysis/figures.py',
                                     '--analysis', str(dest / 'summary.json'), '--output', str(figures)])
            figure_manifest = json.loads((figures / 'manifest.json').read_text())
            expected_figures = ROOT / 'paper/figures' / block
            for name, sha in figure_manifest['files'].items():
                if digest(expected_figures / name) != sha:
                    raise ValueError('Regenerated figure/table differs: ' + block + '/' + name)
            receipt['checks'][block + '_figure_and_table_bytes_identical'] = True
        reference = output / 'sql-reference'
        run('sql-reference', [sys.executable, '-m', 'study.reference', '--data', 'data/study/main-v1',
                              '--output', str(reference)])
        before = [json.loads(line) for line in (ROOT / 'experiments/main/sql-reference/outputs.jsonl').read_text().splitlines()]
        after = [json.loads(line) for line in (reference / 'outputs.jsonl').read_text().splitlines()]
        for rows in [before, after]:
            for row in rows:
                row.pop('policy_seconds', None)
        if before != after:
            raise ValueError('Deterministic policy reference outputs differ')
        receipt['checks']['sql_reference_identical_excluding_timing'] = True
        costs = output / 'cost-accounting.json'
        run('cost-accounting', [sys.executable, 'analysis/cost_accounting.py', '--runs',
            'experiments/main/primary', 'experiments/main/sensitivity', '--output', str(costs)])
        expected_costs = json.loads((ROOT / 'analysis/main/cost-accounting.json').read_text())
        actual_costs = json.loads(costs.read_text())
        for item in [expected_costs, actual_costs]:
            item.pop('created_at', None)
        if expected_costs != actual_costs:
            raise ValueError('Recomputed shared-cost accounting differs')
        receipt['checks']['cost_accounting_identical_excluding_timestamp'] = True
        # Context is scored independently of the saved reader responses. This
        # remains post-hoc analysis of v1, not a new preregistered experiment.
        for block in ['primary', 'sensitivity']:
            context = output / 'context-v1' / block
            run('context-' + block, [sys.executable, 'analysis/separate_context.py',
                '--run', 'experiments/main/' + block, '--output', str(context)])
            expected = ROOT / 'analysis/context-v1' / block
            before = json.loads((expected / 'summary.json').read_text())
            after = json.loads((context / 'summary.json').read_text())
            for item in [before, after]:
                item.pop('created_at', None)
            if before != after or digest(context / 'per-query.jsonl') != digest(expected / 'per-query.jsonl'):
                raise ValueError('Context decomposition differs: ' + block)
        receipt['checks']['context_decomposition_identical_excluding_timestamp'] = True
        # Token counts are actual saved runtime receipts. This path must never
        # contact a model server, fetch upstream code, or recompute embeddings.
        for cap in [1024, 1536, 4096]:
            name = 'reproducible-' + str(cap)
            expected = ROOT / 'analysis/gbrain' / name
            dest = output / 'gbrain' / name
            run('gbrain-' + str(cap), [sys.executable, 'benchmarks/gbrain/analyze.py',
                '--run', 'experiments/gbrain/exploratory-96-v2', '--data', 'data/study/main-v1',
                '--cache', 'experiments/main/primary/embeddings.jsonl',
                '--token-cap', str(cap), '--offline-token-counts', str(expected / 'token-counts.json'),
                '--output', str(dest)])
            for filename in ['summary.json', 'per-query.jsonl', 'token-counts.json']:
                if digest(dest / filename) != digest(expected / filename):
                    raise ValueError('Offline GBrain packet analysis differs: ' + name + '/' + filename)
        table = output / 'context-budget-table.tex'
        run('context-budget-table', [sys.executable, 'benchmarks/gbrain/table.py',
            '--analysis-root', str(output / 'gbrain'), '--output', str(table)])
        for path in [table, table.with_suffix('.json')]:
            if digest(path) != digest(ROOT / 'paper/figures' / path.name):
                raise ValueError('Context budget table differs: ' + path.name)
        receipt['checks']['gbrain_saved_rankings_three_budgets_and_table_identical'] = True
        receipt['fresh_native_gbrain_search'] = False
        external = ROOT / 'data/external/messy-company-v1'
        fetch = json.loads((external / 'FETCH_RECEIPT.json').read_text())
        for entry in fetch['files']:
            path = external / entry['path']
            if (path.is_symlink() or not path.resolve().is_relative_to(external)
                    or digest(path) != entry['sha256'] or path.stat().st_size != entry['bytes']):
                raise ValueError('External development file differs: ' + entry['path'])
        receipt['checks']['external_development_files_verified'] = len(fetch['files'])
        plan = output / 'recommendation-plan'
        run('recommendation-plan', [sys.executable, 'benchmarks/recommendation/run.py',
            '--config', 'benchmarks/recommendation/providers.example.json', '--output', str(plan)])
        before = json.loads((ROOT / 'experiments/recommendation/plan-v2/plan.json').read_text())
        after = json.loads((plan / 'plan.json').read_text())
        for item in [before, after]:
            item.pop('created_at', None)
        if before != after or after['executed']:
            raise ValueError('Prospective recommendation plan differs or executed provider calls')
        receipt['checks']['frontier_pilot_plan_identical_zero_provider_requests'] = True
        # Integrated v3: fresh data regeneration, every packet, every raw response,
        # bootstrap summaries and all final figures. These commands are offline.
        generated_integrated = output / 'integrated-data'
        run('integrated-data', [sys.executable, '-m', 'study.fixtures', '--split', 'test',
            '--worlds', '33', '--seed', '2026102302', '--output', str(generated_integrated)])
        for name in ['inputs.json', 'labels.json']:
            if digest(generated_integrated / name) != digest(ROOT / 'data/integrated/main-v1' / name):
                raise ValueError('Integrated data regeneration differs: ' + name)
        rebuilt_audit = output / 'integrated-audit'
        run('integrated-audit', [sys.executable, 'benchmarks/integrated/audit.py',
            '--data', 'data/integrated/main-v1', '--packets', 'experiments/integrated/main-context-v1',
            '--run', 'experiments/integrated/main-reader-v1', '--output', str(rebuilt_audit)])
        for name in ['audit.json', 'contexts.jsonl']:
            if digest(rebuilt_audit / name) != digest(ROOT / 'analysis/integrated/main-audit-v1' / name):
                raise ValueError('Integrated audit reconstruction differs: ' + name)
        rebuilt_main = output / 'integrated-main'
        run('integrated-analysis', [sys.executable, 'benchmarks/integrated/analyze.py',
            '--run', 'experiments/integrated/main-reader-v1', '--data', 'data/integrated/main-v1',
            '--output', str(rebuilt_main)])
        before = json.loads((ROOT / 'analysis/integrated/main-v1/summary.json').read_text())
        after = json.loads((rebuilt_main / 'summary.json').read_text())
        for item in [before, after]:
            item.pop('created_at', None)
        if before != after:
            raise ValueError('Integrated statistical analysis differs')
        if digest(rebuilt_main / 'per-attempt.jsonl') != digest(ROOT / 'analysis/integrated/main-v1/per-attempt.jsonl'):
            raise ValueError('Integrated per-attempt analysis differs')
        rebuilt_external = output / 'integrated-external'
        run('external-wiki-analysis', [sys.executable, 'benchmarks/integrated/external_analyze.py',
            '--run', 'experiments/integrated/external-reader-v1', '--wiki', 'experiments/integrated/external-wiki-compile-v4',
            '--output', str(rebuilt_external)])
        for name in ['summary.json', 'per-attempt.jsonl']:
            if digest(rebuilt_external / name) != digest(ROOT / 'analysis/integrated/external-v1' / name):
                raise ValueError('External wiki raw-response scoring differs: ' + name)
        rebuilt_chunks = output / 'integrated-chunks'
        run('external-chunked-control', [sys.executable, 'benchmarks/integrated/external_chunks.py',
            '--analyze', 'experiments/integrated/external-chunks-v1', '--output', str(rebuilt_chunks)])
        for name in ['summary.json', 'per-attempt.jsonl']:
            if digest(rebuilt_chunks / name) != digest(ROOT / 'analysis/integrated/external-chunks-v1' / name):
                raise ValueError('External chunked control differs: ' + name)
        sensitivity = output / 'external-sensitivity.json'
        run('external-label-sensitivity', [sys.executable, 'benchmarks/integrated/external_sensitivity.py',
            '--base', str(rebuilt_external / 'per-attempt.jsonl'), '--chunks', str(rebuilt_chunks / 'per-attempt.jsonl'),
            '--output', str(sensitivity)])
        if digest(sensitivity) != digest(ROOT / 'analysis/integrated/external-sensitivity.json'):
            raise ValueError('External label sensitivity differs')
        accounting = output / 'integrated-accounting.json'
        run('integrated-provider-accounting', [sys.executable, 'benchmarks/integrated/accounting.py', '--output', str(accounting)])
        if digest(accounting) != digest(ROOT / 'analysis/integrated/provider-accounting.json'):
            raise ValueError('Integrated provider accounting differs')
        integrated_figures = output / 'integrated-figures'
        run('integrated-figures', [sys.executable, 'benchmarks/integrated/figures.py',
            '--main', str(rebuilt_main / 'summary.json'), '--context', str(rebuilt_audit / 'contexts.jsonl'),
            '--external', str(rebuilt_external / 'summary.json'), '--chunks', str(rebuilt_chunks / 'summary.json'), '--output', str(integrated_figures)])
        fm = json.loads((integrated_figures / 'manifest.json').read_text())
        for name, value in fm['files'].items():
            if digest(ROOT / 'paper/figures/integrated' / name) != value:
                raise ValueError('Integrated figure/table differs: ' + name)
        receipt['checks']['integrated_data_contexts_raw_scores_statistics_figures_identical'] = True
        receipt['checks']['external_wiki_raw_scores_identical'] = True
        mock_execution = output / 'integrated-mock-execution'
        run('integrated-mock-execution', [sys.executable, 'benchmarks/integrated/dry_run.py',
            '--run', 'experiments/integrated/main-reader-v1', '--data', 'data/integrated/main-v1', '--output', str(mock_execution)])
        for name in ['summary.json', 'receipts.jsonl']:
            if digest(mock_execution / name) != digest(ROOT / 'analysis/integrated/main-mock-execution' / name):
                raise ValueError('Mock workflow execution differs: ' + name)
        receipt['checks']['mock_workflows_reexecuted_without_external_actions'] = True
        # V4 challenge: fresh original data, separate oracle, every raw response,
        # every declared request and the generic task-word control. No API calls.
        challenge_index = json.loads((ROOT / 'data/challenge/main-v1/index.json').read_text())
        challenge_generated = output / 'challenge-data'
        run('challenge-data', [sys.executable, '-m', 'benchmarks.challenge.generate',
            '--worlds', str(challenge_index['worlds']), '--seed', str(challenge_index['seed']),
            '--split', challenge_index['split'], '--output', str(challenge_generated)])
        for original in (ROOT / 'data/challenge/main-v1').rglob('*.json'):
            relative = original.relative_to(ROOT / 'data/challenge/main-v1')
            if digest(original) != digest(challenge_generated / relative):
                raise ValueError('Challenge data/labels differ: ' + str(relative))
        for label, command, expected in [
            ('challenge-oracle', ['-m', 'benchmarks.challenge.check_oracle', '--data', 'data/challenge/main-v1'], 'analysis/challenge/main-oracle.json'),
            ('challenge-context-audit', ['analysis/challenge_audit.py', '--data', 'data/challenge/main-v1', '--packets', 'experiments/challenge/main-context-v1'], 'analysis/challenge/main-context-audit.json'),
            ('challenge-trace-audit', ['analysis/challenge_trace_audit.py', '--data', 'data/challenge/main-v1', '--packets', 'experiments/challenge/main-context-v1', '--run', 'experiments/challenge/main-reader-v1', '--freeze', 'experiments/challenge/main-freeze-v1.json'], 'analysis/challenge/main-trace-audit.json'),
            ('challenge-budget', ['analysis/challenge_budget.py', '--data', 'data/challenge/main-v1', '--packets', 'experiments/challenge/main-context-v1'], 'analysis/challenge/main-budget.json'),
            ('challenge-accounting', ['analysis/challenge_accounting.py'], 'analysis/challenge/accounting.json'),
            ('challenge-diagnostics', ['analysis/challenge_diagnostics.py'], 'analysis/challenge/diagnostics.json'),
            ('challenge-native-telemetry', ['analysis/challenge_native_telemetry.py', '--packets', 'experiments/challenge/main-context-v1'], 'analysis/challenge/native-telemetry.json'),
        ]:
            destination = output / (label + '.json')
            run(label, [sys.executable] + command + ['--output', str(destination)])
            if digest(destination) != digest(ROOT / expected):
                raise ValueError('Challenge verification differs: ' + label)
        for context_version in ['pilot-context-v2', 'main-context-v1']:
            run('challenge-embeddings-' + context_version, [sys.executable,
                'scripts/shard_embedding_snapshot.py', 'experiments/challenge/' + context_version + '/embedding-snapshot.json.gz', '--verify'])
        external_opus = output / 'external-opus'
        run('challenge-external-opus', [sys.executable, 'analysis/challenge_external_opus.py',
            '--analyze', 'experiments/challenge/external-opus-v1', '--output', str(external_opus)])
        for name in ['summary.json', 'per-attempt.json']:
            if digest(external_opus / name) != digest(ROOT / 'analysis/challenge/external-opus' / name):
                raise ValueError('External Opus raw-response replay differs: ' + name)
        challenge_results = output / 'challenge-main'
        run('challenge-raw-response-analysis', [sys.executable, '-m', 'benchmarks.challenge.analyze',
            '--data', 'data/challenge/main-v1', '--packets', 'experiments/challenge/main-context-v1',
            '--run', 'experiments/challenge/main-reader-v1', '--output', str(challenge_results)])
        for name in ['summary.json', 'per-attempt.json', 'per-attempt.csv', 'context.json', 'context.csv']:
            if digest(challenge_results / name) != digest(ROOT / 'analysis/challenge/main-v1' / name):
                raise ValueError('Challenge raw-score/statistics reconstruction differs: ' + name)
        challenge_figures = output / 'challenge-figures'
        run('challenge-figures', [sys.executable, 'analysis/challenge_figures.py',
            '--summary', str(challenge_results / 'summary.json'), '--budget', str(output / 'challenge-budget.json'), '--external', str(external_opus / 'summary.json'), '--output', str(challenge_figures)])
        for figure in challenge_figures.iterdir():
            if digest(figure) != digest(ROOT / 'paper/figures/challenge' / figure.name):
                raise ValueError('Challenge figure/table differs: ' + figure.name)
        receipt['checks']['challenge_data_oracles_requests_raw_scores_statistics_controls_figures_identical'] = True
        receipt['checks']['challenge_sharded_embeddings_losslessly_reassembled'] = True
        receipt['fresh_frontier_api_calls'] = 0
        run('report-claims', [sys.executable, 'scripts/verify_report_claims.py'])
        receipt['checks']['numeric_claim_register_and_citation_keys_verified'] = True
        pdf = output / 'report.pdf'
        run('paper', [sys.executable, 'scripts/compile_paper.py', '--output', str(pdf)])
        texts = [subprocess.check_output(['pdftotext', '-layout', str(path), '-'], cwd=ROOT)
                 for path in [ROOT / 'paper/report.pdf', pdf]]
        if texts[0] != texts[1]:
            raise ValueError('Recompiled PDF extracted text/layout differs')
        receipt['checks']['paper_recompiled_and_text_layout_identical'] = True
        receipt['checks']['recompiled_pdf_sha256'] = digest(pdf)
        investor = output / 'investor-note.pdf'
        run('investor-note', [sys.executable, 'scripts/compile_investor_note.py', '--output', str(investor)])
        note_texts = [subprocess.check_output(['pdftotext', '-layout', str(path), '-'], cwd=ROOT)
                      for path in [ROOT / 'paper/investor-note.pdf', investor]]
        if note_texts[0] != note_texts[1]:
            raise ValueError('Recompiled investor-note text/layout differs')
        if digest(investor.with_suffix('.tex')) != digest(ROOT / 'paper/investor-note.tex'):
            raise ValueError('Generated investor-note LaTeX differs')
        receipt['checks']['investor_note_two_pages_and_text_layout_identical'] = True
        if a.upstream_scorer_check:
            diagnostic = output / 'upstream-scorer' / 'report.json'
            run('upstream-scorer', [sys.executable, 'scripts/audit_enterprisemem_scorer.py',
                                   '--output', str(diagnostic)])
            expected_diagnostic = json.loads((ROOT / 'literature/diagnostics/enterprisemem-scorer.json').read_text())
            actual_diagnostic = json.loads(diagnostic.read_text())
            for item in [expected_diagnostic, actual_diagnostic]:
                item.pop('created_at', None)
            if expected_diagnostic != actual_diagnostic:
                raise ValueError('Upstream scorer diagnostic differs')
            receipt['checks']['upstream_scorer_diagnostic_identical_excluding_timestamp'] = True
        if a.fresh_smoke:
            smoke = output / 'fresh-inference-smoke'
            run('fresh-inference-smoke', [sys.executable, '-m', 'study.run',
                '--data', 'data/study/runtime-smoke-v1', '--output', str(smoke),
                '--model-config', 'experiments/qwen3-moe-study.json',
                '--runtime-manifest', 'experiments/qwen3-moe-runtime.json',
                '--embedding-cache', str(output / 'fresh-embeddings.jsonl'),
                '--methods', 'prompt_hybrid', 'typed', '--conditions', 'initial', '--token-cap', '1024'])
            run('fresh-inference-audit', [sys.executable, 'analysis/audit_run.py', '--run', str(smoke),
                '--data', 'data/study/runtime-smoke-v1', '--output', str(output / 'fresh-inference-audit.json')])
            audit = json.loads((output / 'fresh-inference-audit.json').read_text())
            rows = [json.loads(line) for line in (smoke / 'attempts.jsonl').read_text().splitlines()]
            returned = [r for r in rows if r['status'] in ['completed', 'failed'] and 'raw_output' in r]
            if audit['physical_calls'] != 2 or len(returned) != 2 or audit['reused_requests']:
                raise ValueError('Fresh smoke did not retain two actual new model responses')
            receipt['checks']['fresh_inference_requests'] = 2
            receipt['checks']['fresh_inference_reused_requests'] = 0
            receipt['fresh_smoke_accuracy_is_not_main_reproduction'] = True
        for record in manifest['files']:
            if digest(ROOT / record['path']) != record['sha256']:
                raise ValueError('Reproduction modified a packaged evidence file: ' + record['path'])
        if digest(ROOT / 'MANIFEST.json') != manifest_sha256:
            raise ValueError('Reproduction modified the package manifest')
        receipt['checks']['packaged_evidence_unchanged_after_reproduction'] = True
        receipt['passed'] = True
    finally:
        receipt['finished_at'] = datetime.now(timezone.utc).isoformat()
        save()
    print(json.dumps({'passed': True, 'receipt': str(receipt_path), 'core_payload_sha256': core}))


if __name__ == '__main__':
    main()
