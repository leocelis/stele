"""Mnemonic sovereignty proxies (stdlib; no LLM).

Survey gap (arXiv:2604.16548): post-deletion verification and rollback
governance are blind spots. Stele exposes checklist + verify helpers.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError

GOVERNANCE_PRIMITIVES = (
    "write_gate_validation",
    "source_binding",
    "scoped_retrieval",
    "conflict_isolation",
    "non_revival",
    "post_deletion_verify",
    "rollback_plan",
    "share_redaction",
    "forget_accessibility",
)


def sovereignty_checklist(
    *,
    has_write_gate: bool = True,
    has_source_binding: bool = True,
    has_scoped_retrieval: bool = True,
    has_conflict_isolation: bool = True,
    has_non_revival: bool = True,
    has_post_deletion_verify: bool = True,
    has_rollback_plan: bool = True,
    has_share_redaction: bool = True,
    has_forget_accessibility: bool = True,
) -> dict[str, Any]:
    """
    Score coverage of nine mnemonic-sovereignty governance primitives.
    """
    flags = {
        "write_gate_validation": has_write_gate,
        "source_binding": has_source_binding,
        "scoped_retrieval": has_scoped_retrieval,
        "conflict_isolation": has_conflict_isolation,
        "non_revival": has_non_revival,
        "post_deletion_verify": has_post_deletion_verify,
        "rollback_plan": has_rollback_plan,
        "share_redaction": has_share_redaction,
        "forget_accessibility": has_forget_accessibility,
    }
    covered = [k for k, v in flags.items() if v]
    missing = [k for k, v in flags.items() if not v]
    return {
        "primitives": list(GOVERNANCE_PRIMITIVES),
        "flags": flags,
        "covered": covered,
        "missing": missing,
        "coverage": round(len(covered) / len(GOVERNANCE_PRIMITIVES), 4),
        "ok": len(missing) == 0,
        "note": "Mnemonic sovereignty checklist — survey nine primitives",
    }


def post_delete_verify(
    entries: Sequence[Mapping[str, Any]],
    *,
    deleted_ids: Sequence[str],
    search_hits: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Verify deleted IDs are absent from live store and optional Select hits.
    """
    ids = [str(i) for i in deleted_ids if i]
    if not ids:
        raise SchemaError("deleted_ids is required")
    live = {str(e.get("id")) for e in entries}
    still_live = [i for i in ids if i in live]
    hit_ids = {str(h.get("id")) for h in (search_hits or [])}
    still_in_hits = [i for i in ids if i in hit_ids]
    return {
        "deleted_ids": ids,
        "still_live": still_live,
        "still_in_hits": still_in_hits,
        "ok": not still_live and not still_in_hits,
        "note": "post_delete_verify — store + Select absence check",
    }


def rollback_plan(
    entries: Sequence[Mapping[str, Any]],
    *,
    target_ids: Sequence[str],
    reason: str = "operator_rollback",
) -> dict[str, Any]:
    """
    Report-only rollback plan: revoke/supersede targets; never auto-writes.
    """
    reason = str(reason or "").strip() or "operator_rollback"
    ids = [str(i) for i in target_ids if i]
    if not ids:
        raise SchemaError("target_ids is required")
    by_id = {str(e.get("id")): e for e in entries}
    steps: list[dict[str, Any]] = []
    missing: list[str] = []
    for eid in ids:
        e = by_id.get(eid)
        if e is None:
            missing.append(eid)
            continue
        state = str(e.get("state") or "")
        action = "noop"
        if state == "promoted":
            action = "revoke_or_supersede"
        elif state == "contested":
            action = "resolve_then_revoke"
        elif state == "quarantined":
            action = "delete_or_leave"
        steps.append(
            {
                "id": eid,
                "title": e.get("title"),
                "state": state,
                "action": action,
                "reason": reason,
            }
        )
    return {
        "steps": steps,
        "missing": missing,
        "count": len(steps),
        "ok": len(missing) == 0,
        "note": "rollback_plan — report-only; actor must apply revoke/delete",
    }
