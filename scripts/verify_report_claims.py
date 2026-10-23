#!/usr/bin/env python3
"""Verify the numerical claim register and cited keys; no inference or prose grading."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def main():
    register = json.loads((ROOT / 'release/CLAIMS.json').read_text())
    checked = 0
    for claim in register['claims']:
        for quantity in claim.get('quantities', []):
            values = []
            for source in quantity['sources']:
                path = ROOT / source['artifact']
                raw = path.read_bytes()
                if hashlib.sha256(raw).hexdigest() != source['sha256']:
                    raise ValueError('Changed claim source: ' + source['artifact'])
                value = json.loads(raw)
                for key in source['keys']:
                    value = value[key]
                values.append(value)
            operation = quantity.get('operation', 'identity')
            if operation == 'identity' and len(values) == 1:
                actual = values[0]
            elif operation == 'sum':
                actual = sum(values)
            else:
                raise ValueError('Unsupported claim operation')
            if actual != quantity['value']:
                raise ValueError('Numerical claim differs: ' + claim['id'] + '/' + quantity['name'])
            checked += 1
    bibliography = (ROOT / 'paper/references.bib').read_text()
    defined = set(re.findall(r'@\w+\{([^,\s]+)', bibliography))
    verified = {r['key'] for r in json.loads((ROOT / 'sources/bibliography-audit.json').read_text())}
    cited = set()
    for path in (ROOT / 'paper').glob('*.tex'):
        for group in re.findall(r'\\cite(?:t|p)?(?:\[[^\]]*\])*\{([^}]+)\}', path.read_text()):
            cited.update(key.strip() for key in group.split(','))
    if cited - defined or defined - verified:
        raise ValueError('Undefined citation or bibliography entry without verification receipt')
    print(json.dumps({'passed': True, 'quantities_verified': checked,
                      'cited_keys_verified': len(cited), 'bibliography_entries_verified': len(defined),
                      'scope': 'Register values and source hashes plus citation-key provenance. Not automatic verification of prose interpretation, full-text review or scientific validity.'}))


if __name__ == '__main__':
    main()
