"""Replay a real native ranking without allowing any network/model call."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from benchmarks.gbrain.analyze import main

ROOT = Path(__file__).resolve().parents[1]


class OfflineReplayTests(unittest.TestCase):
    def test_all_controls_replay_after_first_retrieval_without_network(self):
        source = ROOT / 'experiments/gbrain/exploratory-96-v2'
        rows = [json.loads(line) for line in (source / 'attempts.jsonl').read_text().splitlines()]
        row = next(r for r in rows if r['status'] == 'completed' and r['gbrain']['context']['answerable'])
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            run = base / 'run'
            (run / row['case_id']).mkdir(parents=True)
            manifest = json.loads((source / 'manifest.json').read_text())
            manifest['planned_cases'] = [row['case_id']]
            manifest['completed'] = 1
            (run / 'manifest.json').write_text(json.dumps(manifest))
            (run / 'attempts.jsonl').write_text(json.dumps(row) + '\n')
            shutil.copyfile(source / row['case_id'] / 'stdout.json', run / row['case_id'] / 'stdout.json')
            argv = ['analyze', '--run', str(run), '--data', str(ROOT / 'data/study/main-v1'),
                    '--cache', str(ROOT / 'experiments/main/primary/embeddings.jsonl'),
                    '--token-cap', '1536', '--offline-token-counts',
                    str(ROOT / 'analysis/gbrain/reproducible-1536/token-counts.json'),
                    '--output', str(base / 'analysis')]
            with patch('sys.argv', argv), patch('urllib.request.urlopen', side_effect=AssertionError('Offline replay contacted network')) as network:
                main()
                network.assert_not_called()
            results = [json.loads(line) for line in (base / 'analysis/per-query.jsonl').read_text().splitlines()]
            self.assertEqual(len(results), 6)
            self.assertTrue(all(r['packed_input_tokens'] <= 1536 for r in results))
            self.assertTrue(all(r['complete_positive_support'] for r in results if r['method'] in ['typed', 'gbrain_catalog_coverage']))


if __name__ == '__main__':
    unittest.main()
