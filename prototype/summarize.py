"""Summarize complete or interrupted attempt ledgers without dropping failures.

Development fixtures never produce inferential confidence intervals or a claim
of empirical superiority. World-level paired differences are descriptive only.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
from statistics import mean

TERMINAL = {"completed", "invalid_output", "failed"}


def summarize(manifest, records):
    cases = manifest["planned_cases"]
    if len({c["case_id"] for c in cases}) != len(cases):
        raise ValueError("Duplicate planned case IDs")
    worlds = {c["case_id"]: c["world"] for c in cases}
    planned = {(c["case_id"], m) for c in cases for m in manifest["methods"]}
    terminal = {}
    for record in records:
        key = (record["case_id"], record["method"])
        if key not in planned or record["world"] != worlds[record["case_id"]]:
            raise ValueError("Attempt outside the registered plan")
        if record["kind"] != manifest["kind"]:
            raise ValueError("Cannot mix deterministic diagnostics and actual model attempts")
        if record["status"] in TERMINAL:
            if key in terminal:
                raise ValueError("Duplicate terminal attempt; retries need a new explicit attempt identity")
            terminal[key] = record
    by_method, per_world = {}, defaultdict(lambda: defaultdict(list))
    for method in manifest["methods"]:
        rows = [terminal.get((c["case_id"], method)) for c in cases]
        decision = [bool(r and r.get("score", {}).get("decision_correct")) for r in rows]
        for case, correct in zip(cases, decision):
            per_world[method][case["world"]].append(int(correct))
        by_method[method] = {
            "planned": len(cases), "terminal_attempts": sum(r is not None for r in rows),
            "missing_or_interrupted": sum(r is None for r in rows),
            "failed": sum(bool(r and r["status"] == "failed") for r in rows),
            "decision_contract_correct": sum(decision),
            "grounded_applicable": sum(bool(r and r.get("score", {}).get("grounded_applicable")) for r in rows),
            "coverage": sum(bool(r and r.get("score", {}).get("coverage")) for r in rows),
            "inappropriate_abstention": sum(bool(r and r.get("score", {}).get("inappropriate_abstention")) for r in rows),
        }
    pairs = {}
    for method in manifest["methods"]:
        if method != "generic_bm25" and "generic_bm25" in per_world:
            deltas = {world: mean(values) - mean(per_world["generic_bm25"][world])
                      for world, values in per_world[method].items()}
            pairs[method + "_minus_generic_bm25"] = {"world_differences": deltas,
                "mean_paired_difference": mean(deltas.values()) if deltas else None,
                "confidence_interval": None,
                "reason": "Development-only authored fixtures; not independent main-study evidence"}
    return {"kind": manifest["kind"], "run_complete": manifest["complete"],
            "planned_attempts": len(planned), "terminal_attempts": len(terminal),
            "independent_human_validated_worlds": 0, "methods": by_method,
            "descriptive_paired_differences": pairs,
            "interpretation": "Software contract diagnostics" if manifest["kind"].startswith("deterministic")
                               else "Actual model development pilot, not a frozen main evaluation"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    manifest = json.loads((args.run / "manifest.json").read_text())
    records = [json.loads(x) for x in (args.run / "attempts.jsonl").read_text().splitlines()]
    result = summarize(manifest, records)
    (args.run / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
