"""Deterministic, authored DEVELOPMENT fixtures; not independent test worlds.

Expected alternatives are specified by scenario rules, not copied from scorer
output. No narratives, performance numbers or human assessments are generated.
"""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import uuid

from .core import Event, Query, Template, canonical

NAMESPACE = uuid.UUID("82fcddc7-d312-442c-8d58-2e020e7c14e7")


def opaque(name):
    return str(uuid.uuid5(NAMESPACE, name))


def build():
    catalog = [
        Template("research_hiring", "pipeline", "team_hiring", "manual_reporting", 2,
                 ("inspect_signal", "select_accounts"), "Hiring may indicate reporting work; this is a hypothesis, not purchase intent."),
        Template("verify_hiring", "pipeline", "team_hiring", "manual_reporting", 3,
                 ("inspect_signal", "verify_role", "select_accounts"), "Verify the buyer role before considering a reporting-oriented Play."),
        Template("research_migration", "pipeline", "system_migration", "integration_risk", 2,
                 ("inspect_signal", "select_accounts"), "A migration may motivate integration research; it does not establish demand."),
        Template("verify_migration", "pipeline", "system_migration", "integration_risk", 3,
                 ("inspect_signal", "verify_role", "select_accounts"), "Check the role and observed migration before proposing further research."),
    ]
    worlds, cases, labels = [], [], []
    for index, (pain, signal, role, geo) in enumerate([
        ("manual_reporting", "team_hiring", "operations_director", "EU"),
        ("integration_risk", "system_migration", "engineering_director", "US"),
    ]):
        world, account = opaque(f"world-{index}"), opaque(f"account-{index}")
        def event(slot, subject, relation, value, authority="observed", day=1, valid_day=None, scopes=("sales",), supersedes=()):
            return Event(opaque(f"{index}-{slot}"), world, subject, relation, value,
                         opaque(f"source-{index}-{slot}"), f"2026-01-{valid_day or day:02d}T00:00:00Z",
                         f"2026-01-{day:02d}T00:00:00Z", authority, scopes, supersedes)
        base = [event("rp", "seller", "approved_role", role, "approved"),
                event("gp", "seller", "approved_geo", geo, "approved"),
                event("ar", account, "account_role", role), event("ag", account, "account_geo", geo),
                event("sig", account, "observed_signal", signal),
                event("pain", "seller", "offering_pain", pain),
                event("proof", "seller", "proof_for_pain", pain, scopes=("sales", "proof"))]
        # The full history is stored once. Every method sees only the shared
        # cutoff-filtered slice; future revisions are not sent to a model.
        base += [event("silence", account, "non_response", "No reply observed; cause unknown.", day=2),
                 event("proposal", "seller", "approved_geo", "EXCLUDED", "proposed", day=2),
                 event("revision", "seller", "approved_role", "different_role", "approved", day=4,
                       supersedes=(base[0].id,)),
                 event("correction", account, "observed_signal", "signal_retracted", day=5, valid_day=2,
                       supersedes=(base[4].id,))]
        for j in range(12):
            base.append(event(f"noise-{j}", opaque(f"unrelated-{index}-{j}"), "meeting_note",
                              f"Pipeline planning note {j}: reporting, integration, hiring and migration remain topics for discussion."))
        worlds.append({"world": world, "events": [asdict(e) for e in base]})
        alternatives = [t.id for t in catalog if t.pain == pain]
        scenarios = [
            ("initial", 1, 1, ("sales", "proof"), alternatives),
            ("weak_feedback", 2, 2, ("sales", "proof"), alternatives),
            ("approved_revision", 4, 4, ("sales", "proof"), []),
            ("late_correction", 2, 5, ("sales", "proof"), []),
            ("no_proof_access", 1, 1, ("sales",), []),
            ("stable_control", 3, 3, ("sales", "proof"), alternatives),
        ]
        for name, valid, known, scopes, expected in scenarios:
            case_id = opaque(f"case-{index}-{name}")
            query = Query(world, account, "pipeline", f"2026-01-{valid:02d}T00:00:00Z",
                          f"2026-01-{known:02d}T00:00:00Z", scopes, 4)
            cases.append({"case_id": case_id, "query": asdict(query)})
            labels.append({"case_id": case_id, "condition": name, "acceptable_templates": expected})
    return {"catalog": [asdict(t) for t in catalog], "worlds": worlds, "cases": cases}, {"labels": labels}


def main():
    root = Path(__file__).resolve().parents[1]
    destination = root / "data/public/dev"
    destination.mkdir(parents=True, exist_ok=True)
    inputs, labels = build()
    entries = {}
    for name, data in [("inputs.json", inputs), ("labels.json", labels)]:
        payload = (json.dumps(data, indent=2) + "\n").encode()
        path = destination / name
        path.write_bytes(payload)
        entries[name] = {"sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)}
    manifest = {"split": "development_only", "generator": "prototype/fixtures.py", "worlds": len(inputs["worlds"]),
                "cases": len(inputs["cases"]), "independent_human_validation": False,
                "model_generation": False, "files": entries}
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(canonical(manifest))


if __name__ == "__main__":
    main()
