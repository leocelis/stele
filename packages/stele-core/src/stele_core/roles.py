"""MemIR-shaped typed roles + D-Mem quality-gated dual channel (stdlib)."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError

MEMORY_ROLES = frozenset({"evidence", "claim", "decision"})

# Default role by layer when memory_role omitted (MemIR-shaped separation).
_LAYER_DEFAULT_ROLE: dict[str, str] = {
    "failure_lesson": "claim",
    "decision": "decision",
    "workflow": "claim",
    "skill_artifact": "claim",
    "goal": "claim",
    "issue": "evidence",
}


def infer_memory_role(entry: Mapping[str, Any]) -> str:
    """Resolve explicit memory_role or layer default."""
    explicit = entry.get("memory_role")
    if explicit:
        role = str(explicit).strip().lower()
        if role not in MEMORY_ROLES:
            raise SchemaError(f"memory_role must be one of {sorted(MEMORY_ROLES)}")
        return role
    layer = str(entry.get("layer") or "")
    return _LAYER_DEFAULT_ROLE.get(layer, "claim")


def project_fact_interface(
    entries: Iterable[Mapping[str, Any]],
    entry_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    """
    MemIR-shaped fact interface: separate evidence / claim / decision atoms.

    Factual authorization for answers should use claims (+ decisions), not raw evidence.
    """
    by_id = {str(e.get("id")): e for e in entries}
    ids = list(entry_ids) if entry_ids is not None else list(by_id.keys())
    evidence: list[dict[str, Any]] = []
    claims: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    missing: list[str] = []
    for eid in ids:
        e = by_id.get(str(eid))
        if e is None:
            missing.append(str(eid))
            continue
        role = infer_memory_role(e)
        atom = {
            "id": e.get("id"),
            "role": role,
            "title": e.get("title"),
            "state": e.get("state"),
            "layer": e.get("layer"),
            "scope": e.get("scope"),
            "source": (e.get("provenance") or {}).get("source"),
        }
        if role == "evidence":
            evidence.append(atom)
        elif role == "decision":
            decisions.append(atom)
        else:
            claims.append(atom)
    return {
        "evidence": evidence,
        "claims": claims,
        "decisions": decisions,
        "missing_ids": missing,
        "claim_ids": [c["id"] for c in claims],
        "authorize_ids": [c["id"] for c in claims] + [d["id"] for d in decisions],
        "note": "MemIR-shaped typed roles — authorize from claims/decisions, not evidence alone",
    }


def role_collapse_scan(
    entries: Iterable[Mapping[str, Any]],
    *,
    limit: int = 50,
) -> dict[str, Any]:
    """
    Detect provenance-role collapse suspects (report-only).

    Heuristic: evidence-role entries that are promoted without external evidence list,
    or claim-role entries with agent=pack-hydrate treated as authoritative without cap note.
    """
    if limit < 1:
        raise SchemaError("limit must be >= 1")
    suspects: list[dict[str, Any]] = []
    for e in entries:
        if len(suspects) >= limit:
            break
        role = infer_memory_role(e)
        state = str(e.get("state") or "")
        prov = e.get("provenance") or {}
        agent = str(prov.get("agent") or "")
        has_ev = bool(e.get("evidence"))
        reasons: list[str] = []
        if role == "evidence" and state == "promoted" and not has_ev:
            reasons.append("evidence_role_promoted_without_evidence_list")
        if role == "claim" and agent == "pack-hydrate" and state == "promoted":
            reasons.append("claim_from_pack_hydrate")
        if role == "decision" and not has_ev and state == "promoted":
            reasons.append("decision_without_evidence")
        if reasons:
            suspects.append(
                {
                    "id": e.get("id"),
                    "role": role,
                    "state": state,
                    "agent": agent,
                    "reasons": reasons,
                }
            )
    return {
        "suspects": suspects,
        "count": len(suspects),
        "note": "heuristic role-collapse scan — not a neural source-monitor",
    }


def quality_gate(
    hits: Sequence[Mapping[str, Any]],
    *,
    min_hits: int = 1,
    require_claim: bool = True,
    escalate_on_contested_flag: bool = True,
) -> dict[str, Any]:
    """
    D-Mem-shaped multi-dimensional quality gate (deterministic).

    Routine channel OK when enough claim-role hits without contested flags;
    else escalate to deliberation.
    """
    reasons: list[str] = []
    claim_hits = [h for h in hits if str(h.get("memory_role") or "claim") in {"claim", "decision"}]
    if require_claim and len(claim_hits) < min_hits:
        reasons.append("insufficient_claim_hits")
    if len(hits) < min_hits:
        reasons.append("insufficient_hits")
    contested_flags = [
        h for h in hits if h.get("contested") or str(h.get("state") or "") == "contested"
    ]
    if escalate_on_contested_flag and contested_flags:
        reasons.append("contested_in_hits")
    injection = [h for h in hits if h.get("injection_suspect")]
    if injection:
        reasons.append("injection_suspect_in_hits")
    routine_ok = len(reasons) == 0
    return {
        "routine_ok": routine_ok,
        "escalate_deliberation": not routine_ok,
        "reasons": reasons,
        "hit_count": len(hits),
        "claim_hit_count": len(claim_hits),
        "note": "D-Mem-shaped quality gate — no LLM judge",
    }
