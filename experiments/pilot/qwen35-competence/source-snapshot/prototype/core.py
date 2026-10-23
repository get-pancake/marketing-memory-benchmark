"""Shared causal input boundary, reference retrieval and structured scorer.

No model or network calls occur here. The policy reference is a diagnostic,
not a language-model baseline. All methods receive the same verified events.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import json
import math
import re
from collections import Counter
from typing import Iterable


def timestamp(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("All timestamps must include a timezone")
    return result


@dataclass(frozen=True)
class Event:
    id: str
    world: str
    subject: str
    relation: str
    value: str
    source: str
    valid_from: str
    observed_at: str
    authority: str
    scopes: tuple[str, ...]
    supersedes: tuple[str, ...] = ()

    def __post_init__(self):
        timestamp(self.valid_from)
        timestamp(self.observed_at)
        if self.authority not in {"approved", "observed", "proposed", "hypothesis"}:
            raise ValueError("Unknown authority")
        if not all(isinstance(x, str) and x for x in
                   (self.id, self.world, self.subject, self.relation, self.value, self.source)):
            raise ValueError("Event identifiers and values must be nonempty strings")
        object.__setattr__(self, "scopes", tuple(self.scopes))
        object.__setattr__(self, "supersedes", tuple(self.supersedes))


@dataclass(frozen=True)
class Query:
    world: str
    account: str
    objective: str
    valid_at: str
    known_at: str
    scopes: tuple[str, ...]
    max_units: int

    def __post_init__(self):
        timestamp(self.valid_at)
        timestamp(self.known_at)
        if type(self.max_units) is not int or self.max_units < 0:
            raise ValueError("max_units must be a nonnegative integer")
        object.__setattr__(self, "scopes", tuple(self.scopes))


@dataclass(frozen=True)
class Template:
    id: str
    objective: str
    signal: str
    pain: str
    units: int
    capabilities: tuple[str, ...]
    mechanism: str

    def __post_init__(self):
        if type(self.units) is not int or self.units < 0:
            raise ValueError("Template units must be a nonnegative integer")
        object.__setattr__(self, "capabilities", tuple(self.capabilities))


POLICY_RELATIONS = {"approved_role", "approved_geo"}
REQUIRED_RELATIONS = {"approved_role", "approved_geo", "account_role", "account_geo",
                      "observed_signal", "offering_pain", "proof_for_pain"}
METHODS = ("generic_bm25", "prompt_specialized", "typed_coverage", "full_context")


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def visible_events(events: Iterable[Event], query: Query) -> list[Event]:
    """Shared input boundary: world, observed time, valid time and all required scopes.

    This is an explicit-entitlement fixture model, not a production ACL system.
    Visibility is enforced before indexing. Proposals never supersede approved
    strategy; conflicting approved values remain visible for the planner to reject.
    """
    events = list(events)
    ids = [e.id for e in events]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate event IDs")
    by_id = {e.id: e for e in events}
    for event in events:
        for previous_id in event.supersedes:
            if previous_id not in by_id:
                raise ValueError("Supersession target missing")
            previous = by_id[previous_id]
            if (previous.world, previous.subject, previous.relation, previous.authority) != (
                    event.world, event.subject, event.relation, event.authority):
                raise ValueError("Supersession must preserve world, subject, relation and authority")
            if timestamp(previous.observed_at) >= timestamp(event.observed_at):
                raise ValueError("Supersession must be strictly later in observed time")
    eligible = [e for e in events if e.world == query.world
                and timestamp(e.observed_at) <= timestamp(query.known_at)
                and timestamp(e.valid_from) <= timestamp(query.valid_at)
                and set(e.scopes).issubset(query.scopes)]
    superseded = {old for e in eligible for old in e.supersedes}
    return sorted((e for e in eligible if e.id not in superseded), key=lambda e: e.id)


def words(text: str) -> list[str]:
    return re.findall(r"[\w]+", text.lower())


def retrieve(events: list[Event], query: Query, catalog: list[Template],
             method: str, max_bytes: int) -> list[Event]:
    """BM25 reference, prompt-only control, typed coverage and full-context control.

    The byte budget is exact UTF-8 serialized evidence size, not a token estimate.
    Both lexical controls retrieve identically; their planner instructions differ.
    Full-context fails explicitly when the whole record cannot fit.
    """
    if method not in METHODS or type(max_bytes) is not int or max_bytes < 2:
        raise ValueError("Invalid method or evidence byte budget")
    eligible = visible_events(events, query)
    if method == "full_context":
        if len(canonical([asdict(e) for e in eligible]).encode()) > max_bytes:
            raise ValueError("Full-context record exceeds the declared budget; not truncated")
        return eligible
    documents = [words(canonical(asdict(e))) for e in eligible]
    terms = set(words(query.account + " " + query.objective + " " + " ".join(
        f"{t.signal} {t.pain} {t.mechanism}" for t in catalog if t.objective == query.objective)))
    n = len(documents)
    mean = sum(map(len, documents)) / max(n, 1)
    df = Counter(term for doc in documents for term in set(doc))
    scores = {}
    for event, doc in zip(eligible, documents):
        tf = Counter(doc)
        scores[event.id] = sum(math.log(1 + (n - df[t] + .5) / (df[t] + .5))
                              * tf[t] * 2.2 / (tf[t] + 1.2 * (.25 + .75 * len(doc) / max(mean, 1)))
                              for t in terms if tf[t])
    ranked = sorted(eligible, key=lambda e: (-scores[e.id], e.id))
    if method == "typed_coverage":
        # Uses public relation types and query entities, never evaluator labels.
        relevant = [e for e in ranked if e.relation in REQUIRED_RELATIONS
                    and (e.subject == query.account or e.subject == "seller")]
        selected = []
        seen = set()
        for event in relevant:
            key = (event.subject, event.relation, event.authority)
            if key not in seen:
                selected.append(event)
                seen.add(key)
        prioritized = {e.id for e in selected}
        ranked = selected + [e for e in ranked if e.id not in prioritized]
    output = []
    for event in ranked:
        if len(canonical([asdict(e) for e in output + [event]]).encode()) <= max_bytes:
            output.append(event)
    return output


def support_sets(events: list[Event], query: Query, catalog: list[Template]) -> dict[str, set[str]]:
    """Independent, explicit contract for applicable catalog alternatives.

    Ambiguous facts cause abstention, not arbitrary latest-ID selection. Only
    approved policy and observed account/offer evidence support an action.
    """
    def fact(subject, relation, authority):
        matches = [e for e in events if (e.subject, e.relation, e.authority) ==
                   (subject, relation, authority)]
        if len({e.value for e in matches}) != 1:
            return None
        return sorted(matches, key=lambda e: e.id)[0] if matches else None
    slots = {
        "role_policy": fact("seller", "approved_role", "approved"),
        "geo_policy": fact("seller", "approved_geo", "approved"),
        "role": fact(query.account, "account_role", "observed"),
        "geo": fact(query.account, "account_geo", "observed"),
        "signal": fact(query.account, "observed_signal", "observed"),
        "pain": fact("seller", "offering_pain", "observed"),
        "proof": fact("seller", "proof_for_pain", "observed"),
    }
    if any(e is None for e in slots.values()):
        return {}
    if slots["role"].value != slots["role_policy"].value or slots["geo"].value != slots["geo_policy"].value:
        return {}
    return {t.id: {e.id for e in slots.values()}
            for t in catalog if t.objective == query.objective and t.units <= query.max_units
            and t.signal == slots["signal"].value and t.pain == slots["pain"].value
            and t.pain == slots["proof"].value}


def policy_reference(events: list[Event], query: Query, catalog: list[Template]) -> dict:
    """Executable decision reference over supplied verified events; not an LLM."""
    supports = support_sets(events, query, catalog)
    remaining = query.max_units
    selected = []
    for tid, ids in sorted(supports.items()):
        units = next(t.units for t in catalog if t.id == tid)
        if units <= remaining and len(selected) < 2:
            selected.append({"template_id": tid, "source_ids": sorted(ids), "allowed_next_step": "dry_run"})
            remaining -= units
    return {"status": "recommend" if selected else "request_evidence", "account": query.account,
            "objective": query.objective, "plays": [
                play for play in selected]}


def score(output: object, events: list[Event], supplied: list[Event], query: Query,
          catalog: list[Template], expected_alternatives: list[str]) -> dict:
    """No free-text keyword grading. Fixed case denominator belongs to aggregation.

    Label alternatives must agree with the contract before a result can be scored.
    This is software consistency checking, not independent human validation.
    Cited event IDs must be current, visible, supplied, and sufficient. Human
    strategic usefulness and commercial value are deliberately not scored.
    """
    truth = support_sets(visible_events(events, query), query, catalog)
    if set(expected_alternatives) != set(truth):
        raise ValueError("Fixture labels disagree with independently evaluated action contract")
    result = {"valid_schema": False, "grounded_applicable": False, "decision_correct": False,
              "coverage": False, "inappropriate_abstention": False, "violations": []}
    keys = {"status", "account", "objective", "plays"}
    if not isinstance(output, dict) or set(output) != keys:
        result["violations"].append("schema")
        return result
    if not isinstance(output["status"], str) or output["status"] not in {"recommend", "request_evidence"} or not isinstance(output["plays"], list):
        result["violations"].append("schema")
        return result
    plays = output["plays"]
    if (output["account"], output["objective"]) != (query.account, query.objective):
        result["violations"].append("query_mismatch")
    if len(plays) > 2 or (output["status"] == "recommend") != bool(plays):
        result["violations"].append("status_or_count")
    seen = set()
    supplied_ids = {e.id for e in supplied}
    current_ids = {e.id for e in visible_events(events, query)}
    for play in plays:
        if not isinstance(play, dict) or set(play) != {"template_id", "source_ids", "allowed_next_step"}:
            result["violations"].append("schema")
            continue
        tid, cited = play["template_id"], play["source_ids"]
        if not isinstance(tid, str) or not isinstance(cited, list) or any(not isinstance(x, str) for x in cited):
            result["violations"].append("schema")
            continue
        if len(cited) != len(set(cited)):
            result["violations"].append("duplicate_citation")
        if tid in seen:
            result["violations"].append("duplicate_play")
        seen.add(tid)
        if tid not in truth:
            result["violations"].append("inapplicable_play")
        if not set(cited).issubset(supplied_ids & current_ids):
            result["violations"].append("unavailable_citation")
        cited_events = [e for e in supplied if e.id in cited and e.id in current_ids]
        if tid in truth and tid not in support_sets(cited_events, query, catalog):
            result["violations"].append("insufficient_support")
        if play["allowed_next_step"] != "dry_run":
            result["violations"].append("action_exceeds_permission")
    units = sum(t.units for t in catalog if t.id in seen)
    if units > query.max_units:
        result["violations"].append("resource_limit")
    result["valid_schema"] = "schema" not in result["violations"]
    result["coverage"] = bool(plays)
    result["inappropriate_abstention"] = bool(truth) and not plays
    result["grounded_applicable"] = bool(plays) and not result["violations"]
    result["decision_correct"] = not result["violations"] and (bool(plays) if truth else not plays)
    return result


def dry_run(output: dict, score_result: dict, catalog: list[Template]) -> dict:
    """Mock provider plan only: no external side effects or efficacy claim."""
    if not score_result["grounded_applicable"]:
        return {"kind": "mock_capability_dry_run", "status": "not_executable", "steps": [], "units": 0}
    by_id = {t.id: t for t in catalog}
    return {"kind": "mock_capability_dry_run", "status": "validated",
            "steps": [{"template_id": p["template_id"], "capabilities": list(by_id[p["template_id"]].capabilities)}
                      for p in output["plays"]],
            "units": sum(by_id[p["template_id"]].units for p in output["plays"])}
