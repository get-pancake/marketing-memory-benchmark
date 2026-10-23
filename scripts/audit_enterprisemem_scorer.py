#!/usr/bin/env python3
"""Reproduce narrow scoring diagnostics, NOT a memory/model benchmark.

Uses the inspected MIT-licensed upstream scorer at a fixed, hash-checked revision.
No upstream files are modified, and no model/API calls are made.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path

import research_sources
from research_sources import ROOT, retrieve

REVISION = "819a8bc99db576a21828c2a8e6d273ae2ff023c4"
BASE = f"https://raw.githubusercontent.com/enterprisemem-bench/enterprisemem-bench/{REVISION}/"
SOURCES = {
    "evaluation/eval_kar.py": "5a3e3f78c0acbd48356b7ac885467e5f81d0b536ee06bcb0aecfb6f682913d44",
    "data/finance/questions_10.jsonl": "ec8bad3e21bfb003497471092b604559b30176b5ddb235d433106320fea547be",
    "data/finance/ground_truth_10.jsonl": "6081bc4d84fbd8f32d8e8a3eb41863306847dd1d5e0a537ec1f1fb612ed3dd51",
}


def source(name):
    url = BASE + name
    path = ROOT / ".cache/literature" / (hashlib.sha256(url.encode()).hexdigest()[:20] + ".txt")
    if not path.exists():
        result = retrieve(url)
        if result["status"] != "retrieved":
            raise RuntimeError(f"Required source unavailable: {name}")
    if hashlib.sha256(path.read_bytes()).hexdigest() != SOURCES[name]:
        raise RuntimeError(f"Source checksum mismatch: {name}")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True,
                        help='New report path; never overwrite the archived diagnostic.')
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit('Output exists; select a new report path.')
    output.parent.mkdir(parents=True, exist_ok=True)
    # Download receipts belong beside this new report, not in the distributed
    # historical literature ledger. Upstream bytes remain a checked cache.
    research_sources.LOG = output.with_name(output.stem + '-retrievals.jsonl')
    loader = importlib.machinery.SourceFileLoader("inspected_enterprisemem_scorer", str(source("evaluation/eval_kar.py")))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    questions = [json.loads(line) for line in source("data/finance/questions_10.jsonl").read_text().splitlines()]
    truth = {r["question_id"]: r for r in map(json.loads, source("data/finance/ground_truth_10.jsonl").read_text().splitlines())}
    probes = [
        ("correct_numeric_control", "Q082", "425.0", True),
        ("wrong_numeric_control", "Q082", "400.0", False),
        ("negated_numeric_answer", "Q082", "The budget is not 425.0; the current budget is 400.0.", False),
        ("unit_mismatch", "Q082", "$425.0 billion", False),
        ("negated_categorical_answer", "Q092", "The claim 'No; discontinued' is false. It remains active.", False),
    ]
    results = []
    for name, qid, answer, semantically_correct in probes:
        results.append({"probe": name, "question_id": qid, "authored_answer": answer,
                        "expected_answer": truth[qid]["expected_answer"],
                        "authored_probe_should_be_correct": semantically_correct,
                        "upstream_accepted": module.score_answer(answer, truth[qid])})
    l2 = [q for q in questions if q["level"] == "L2"]
    module.load_questions = lambda level="L2": [q for q in questions if q["level"] == level]
    module.load_ground_truth = lambda: truth
    first = l2[0]["question_id"]
    coverage_probe = module.eval_kar({first: truth[first]["expected_answer"]})
    report = {
        "kind": "deterministic_upstream_scorer_diagnostic_not_model_evaluation",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "upstream_repository": "https://github.com/enterprisemem-bench/enterprisemem-bench",
        "upstream_revision": REVISION, "source_sha256": SOURCES,
        "code_license": "MIT", "data_license": "CC-BY-4.0",
        "probes": results,
        "omission_probe": {"released_subset_l2_count": len(l2), "submitted_count": 1,
                           "reported_kar": coverage_probe["kar"],
                           "reported_denominator": coverage_probe["total"]},
        "interpretation": "Narrow constructed counterexamples; not evidence that upstream model runs exploited these behaviors. Overall accuracy uses a different, fixed denominator. No upstream model result was reproduced.",
    }
    with output.open('x') as stream:
        stream.write(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
