"""Tamper-resistance checks on copies of saved traces; no model requests."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from analysis.audit_run import audit
from study.contract import canonical

ROOT = Path(__file__).resolve().parents[1]


class PromptAuditTest(unittest.TestCase):
    def check(self, mutation=None):
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()):
            dest = Path(temporary) / 'copied-run'
            shutil.copytree(ROOT / 'experiments/pilot/cache-smoke', dest)
            ledger = dest / 'attempts.jsonl'
            rows = [json.loads(line) for line in ledger.read_text().splitlines()]
            if mutation:
                mutation(rows)
                ledger.write_text(''.join(canonical(row) + '\n' for row in rows))
            output = Path(temporary) / 'audit.json'
            audit(dest, ROOT / 'data/study/runtime-smoke-v1', output)
            return json.loads(output.read_text())

    def test_saved_actual_requests_reconstruct_without_model_calls(self):
        result = self.check()
        self.assertEqual(result['reconstructed_inputs'], 2)
        self.assertEqual(result['reconstructed_requests'], 2)
        self.assertEqual(result['physical_calls'], 1)

    def test_forged_fact_with_valid_identifier_and_rehashed_request_rejected(self):
        def mutate(rows):
            for row in rows:
                if 'messages' not in row:
                    continue
                payload = json.loads(row['messages'][1]['content'])
                payload['evidence'][0][3] = 'fabricated fixture value'
                row['messages'][1]['content'] = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
                row['prompt_sha256'] = hashlib.sha256(canonical(row['messages']).encode()).hexdigest()
                request = json.loads(row['request_json'])
                request['messages'] = row['messages']
                row['request_json'] = json.dumps(request, ensure_ascii=False, separators=(',', ':'))
                row['request_sha256'] = hashlib.sha256(row['request_json'].encode()).hexdigest()
        with self.assertRaisesRegex(ValueError, 'prompt content differs'):
            self.check(mutate)

    def test_rehashed_changed_decoding_setting_rejected(self):
        def mutate(rows):
            for row in rows:
                if 'request_json' not in row:
                    continue
                request = json.loads(row['request_json'])
                request['temperature'] = 0.7
                row['request_json'] = json.dumps(request, ensure_ascii=False, separators=(',', ':'))
                row['request_sha256'] = hashlib.sha256(row['request_json'].encode()).hexdigest()
        with self.assertRaisesRegex(ValueError, 'serialized request differs'):
            self.check(mutate)

    def test_duplicate_physical_start_rejected(self):
        def mutate(rows):
            rows.append(next(r for r in rows if r['status'] == 'model_call_started').copy())
        with self.assertRaisesRegex(ValueError, 'duplicate physical-call start'):
            self.check(mutate)


if __name__ == '__main__':
    unittest.main()
