"""Knowledge/Memory/Wisdom/Intelligence persistence layers (stdlib; no LLM).

Shaped by arXiv:2604.11364 — different persistence semantics per layer:
Knowledge = indefinite supersession (no decay); Memory = Ebbinghaus decay;
Wisdom = evidence-gated revision; Intelligence = ephemeral (do not persist).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError

LAYERS = frozenset({"knowledge", "memory", "wisdom", "intelligence"})

# Stele content layers → persistence semantics (heuristic defaults)
_CONTENT_TO_PERSIST: dict[str, str] = {
    "goal": "knowledge",
    "issue": "memory",
    "decision": "knowledge",
    "failure-lesson": "wisdom",
    "workflow": "wisdom",
    "skill": "wisdom",
}


def classify_persistence_layer(
    entry: Mapping[str, Any],
    *,
    override: str | None = None,
) -> dict[str, Any]:
    """
    Map an entry to a persistence-semantics layer.

    Override may set explicit layer; else content `layer` + body heuristics.
    """
    if not isinstance(entry, Mapping):
        raise SchemaError("entry mapping is required")
    if override is not None:
        layer = str(override).strip().lower()
        if layer not in LAYERS:
            raise SchemaError(f"override must be one of {sorted(LAYERS)}")
    else:
        meta = entry.get("assessment") or {}
        if isinstance(meta, Mapping) and meta.get("persistence_layer"):
            layer = str(meta.get("persistence_layer")).strip().lower()
            if layer not in LAYERS:
                layer = "memory"
        else:
            content = str(entry.get("layer") or "").strip().lower()
            layer = _CONTENT_TO_PERSIST.get(content, "memory")
            body = f"{entry.get('title') or ''}\n{entry.get('body') or ''}".lower()
            if "ephemeral" in body or "do not persist" in body or "session only" in body:
                layer = "intelligence"
            elif "policy" in body or "canonical fact" in body or "invariant" in body:
                layer = "knowledge"

    decay_ok = layer == "memory"
    supersede_ok = layer in {"knowledge", "wisdom", "memory"}
    persist_ok = layer != "intelligence"
    evidence_gate = layer == "wisdom"

    return {
        "id": entry.get("id"),
        "persistence_layer": layer,
        "decay_allowed": decay_ok,
        "supersession_allowed": supersede_ok,
        "persist_allowed": persist_ok,
        "evidence_gated_revision": evidence_gate,
        "ok": True,
        "note": "knowledgelayer classify_persistence_layer — persistence semantics",
    }


def persistence_policy(layer: str) -> dict[str, Any]:
    """Policy card for one persistence layer."""
    layer = str(layer or "").strip().lower()
    if layer not in LAYERS:
        raise SchemaError(f"layer must be one of {sorted(LAYERS)}")
    policies = {
        "knowledge": {
            "decay": "none",
            "update": "supersede",
            "ttl": None,
            "summary": "Indefinite supersession; never fade by age alone",
        },
        "memory": {
            "decay": "ebbinghaus",
            "update": "reinforce_or_fade",
            "ttl": "half_life",
            "summary": "Experiential; decay unless reinforced",
        },
        "wisdom": {
            "decay": "slow",
            "update": "evidence_gated",
            "ttl": None,
            "summary": "Lessons revise only with external evidence",
        },
        "intelligence": {
            "decay": "immediate",
            "update": "ephemeral",
            "ttl": "session",
            "summary": "Inference residue — do not persist to SoT",
        },
    }
    return {
        "persistence_layer": layer,
        "policy": policies[layer],
        "ok": True,
        "note": "knowledgelayer persistence_policy",
    }


def layer_inventory(
    entries: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Count entries by persistence layer."""
    counts = {k: 0 for k in sorted(LAYERS)}
    rows: list[dict[str, Any]] = []
    for e in entries:
        if not isinstance(e, Mapping):
            continue
        c = classify_persistence_layer(e)
        pl = str(c["persistence_layer"])
        counts[pl] = counts.get(pl, 0) + 1
        rows.append(
            {
                "id": e.get("id"),
                "persistence_layer": pl,
                "content_layer": e.get("layer"),
                "state": e.get("state"),
            }
        )
    return {
        "counts": counts,
        "entries": rows,
        "total": len(rows),
        "ok": True,
        "note": "knowledgelayer layer_inventory",
    }


def knowledge_protect_scan(
    entries: Sequence[Mapping[str, Any]],
    *,
    faded_ids: Sequence[str] | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """
    Flag knowledge-layer entries that should not be age-faded.

    faded_ids = optional set from fade_scan / archive candidates.
    """
    if limit < 1:
        raise SchemaError("limit must be >= 1")
    faded = {str(i) for i in (faded_ids or []) if i}
    violations: list[dict[str, Any]] = []
    for e in entries:
        if not isinstance(e, Mapping):
            continue
        c = classify_persistence_layer(e)
        if c["persistence_layer"] != "knowledge":
            continue
        eid = str(e.get("id") or "")
        if faded and eid in faded:
            violations.append(
                {
                    "id": eid,
                    "reason": "knowledge_in_fade_set",
                    "title": e.get("title"),
                }
            )
        elif not c["decay_allowed"] and e.get("state") == "archived":
            violations.append(
                {
                    "id": eid,
                    "reason": "knowledge_archived",
                    "title": e.get("title"),
                }
            )
        if len(violations) >= limit:
            break
    return {
        "violations": violations,
        "count": len(violations),
        "ok": True,
        "note": "knowledgelayer knowledge_protect_scan — no age-fade on knowledge",
    }


def intelligence_reject_gate(
    candidate: Mapping[str, Any],
) -> dict[str, Any]:
    """Reject candidates classified as intelligence (ephemeral — do not ADD)."""
    c = classify_persistence_layer(candidate)
    if c["persistence_layer"] == "intelligence" or not c["persist_allowed"]:
        decision = "reject"
        reason = "ephemeral_intelligence"
    else:
        decision = "admit"
        reason = "persistable_layer"
    return {
        "decision": decision,
        "reason": reason,
        "persistence_layer": c["persistence_layer"],
        "ok": True,
        "note": "knowledgelayer intelligence_reject_gate — session residue ≠ SoT",
    }
