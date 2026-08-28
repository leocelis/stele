"""TOKI-shaped write-operator contract + anomaly probes (stdlib; no LLM).

Contradiction resolution is write-time concurrency control. Stele keeps the
judge OFF the core write path; this module classifies intended operators and
reports anomaly proxies (replay / belief-drift / audit erasure).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from stele_core.execution import authority_score
from stele_core.schema import SchemaError

OPERATORS = frozenset(
    {
        "last_writer_wins",
        "evidence_weighted",
        "await_confirmation",
        "per_rule_policy",
    }
)


def classify_write_operator(
    tip: Mapping[str, Any] | None,
    candidate: Mapping[str, Any],
    *,
    evidence: Sequence[Mapping[str, Any]] | None = None,
    policy_rule: str | None = None,
) -> dict[str, Any]:
    """
    Type an incoming write against the four TOKI heuristics.

    Returns operator name, isolation precondition, and audit-row expectation.
    Does not execute the write.
    """
    if not candidate:
        raise SchemaError("candidate is required")
    ev = list(evidence or [])
    has_evidence = bool(ev) or bool(candidate.get("evidence"))
    cand_key = str(candidate.get("conflict_key") or "").strip()
    tip_key = str((tip or {}).get("conflict_key") or "").strip() if tip else ""
    same_key = bool(tip and cand_key and tip_key and cand_key == tip_key)

    if policy_rule:
        op = "per_rule_policy"
        isolation = "policy_precondition"
        reason = f"explicit policy_rule={policy_rule}"
    elif tip is None or not same_key:
        op = "last_writer_wins"
        isolation = "append_only"
        reason = "no same-key tip — treat as fresh write"
    elif not has_evidence:
        op = "await_confirmation"
        isolation = "quarantine_until_evidence"
        reason = "same-key tip present without evidence → await confirmation"
    else:
        tip_auth = authority_score(tip)["authority"]
        cand_auth = authority_score(candidate)["authority"]
        if cand_auth + 0.05 >= tip_auth:
            op = "evidence_weighted"
            isolation = "evidenced_supersede"
            reason = "candidate authority competitive with tip under evidence"
        else:
            op = "await_confirmation"
            isolation = "quarantine_until_stronger_evidence"
            reason = "candidate weaker than tip — await stronger confirmation"

    audit_row_required = op in {
        "last_writer_wins",
        "evidence_weighted",
        "per_rule_policy",
    } and same_key

    return {
        "operator": op,
        "isolation_precondition": isolation,
        "audit_row_required": audit_row_required,
        "same_conflict_key": same_key,
        "tip_id": (tip or {}).get("id"),
        "candidate_title": candidate.get("title"),
        "reason": reason,
        "note": "TOKI-shaped operator plan — judge stays off write path",
    }


def anomaly_scan(
    entries: Iterable[Mapping[str, Any]],
    *,
    journal_rows: Sequence[Mapping[str, Any]] | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """
    Report proxies for TOKI's three write-time anomalies.

    - audit_erasure: superseded without superseded_by / lineage link
    - belief_drift: multiple promoted actives under one conflict_key
    - replay_inconsistency: journal SUPERSEDE refs missing from SoT (if journal given)
    """
    entries_list = list(entries)
    by_id = {str(e.get("id")): e for e in entries_list}
    findings: list[dict[str, Any]] = []

    # audit erasure proxy
    for e in entries_list:
        if e.get("state") != "superseded":
            continue
        sid = str(e.get("id"))
        # Prefer explicit supersede pointer on temporal / links
        temporal = e.get("temporal") or {}
        has_ptr = bool(temporal.get("superseded_by") or temporal.get("superseded_at"))
        linked = False
        for other in entries_list:
            if other.get("id") == sid:
                continue
            for lnk in other.get("links") or []:
                if lnk.get("kind") == "entry" and str(lnk.get("ref")) == sid:
                    linked = True
                    break
            if str(other.get("supersedes") or "") == sid:
                linked = True
            if linked:
                break
        # Also accept journal-style: any promoted with same conflict_key and later id
        same_key_newer = False
        key = str(e.get("conflict_key") or "")
        if key:
            for other in entries_list:
                if other.get("id") == sid:
                    continue
                if str(other.get("conflict_key") or "") != key:
                    continue
                if other.get("state") in {"promoted", "contested", "superseded"}:
                    same_key_newer = True
                    break
        if not (has_ptr or linked or same_key_newer):
            findings.append(
                {
                    "anomaly": "audit_erasure",
                    "entry_id": sid,
                    "detail": "superseded without recoverable successor pointer",
                }
            )

    # belief drift: >1 promoted under same key
    by_key: dict[str, list[str]] = {}
    for e in entries_list:
        if e.get("state") != "promoted":
            continue
        key = str(e.get("conflict_key") or "")
        if not key:
            continue
        by_key.setdefault(key, []).append(str(e.get("id")))
    for key, ids in sorted(by_key.items()):
        if len(ids) > 1:
            findings.append(
                {
                    "anomaly": "belief_drift",
                    "conflict_key": key,
                    "promoted_ids": ids,
                    "detail": "multiple promoted actives under one key",
                }
            )

    # replay inconsistency from journal SUPERSEDE ops
    for row in journal_rows or []:
        op = str(row.get("op") or "")
        if op not in {"SUPERSEDE", "RESOLVE_CONTESTED"}:
            continue
        entry_id = str(row.get("entry_id") or row.get("id") or "")
        if entry_id and entry_id not in by_id:
            findings.append(
                {
                    "anomaly": "replay_inconsistency",
                    "entry_id": entry_id,
                    "op": op,
                    "detail": "journal SUPERSEDE target missing from SoT",
                }
            )

    findings = findings[: max(1, int(limit))]
    by_type: dict[str, int] = {}
    for f in findings:
        by_type[f["anomaly"]] = by_type.get(f["anomaly"], 0) + 1
    return {
        "findings": findings,
        "count": len(findings),
        "by_type": by_type,
        "ok": len(findings) == 0,
        "note": "TOKI anomaly proxies — not paper LoCoMo deltas",
    }


def tip_for_conflict_key(
    entries: Iterable[Mapping[str, Any]], conflict_key: str
) -> dict[str, Any] | None:
    """Best tip under conflict_key: promoted preferred, else contested, else newest."""
    key = str(conflict_key).strip()
    if not key:
        return None
    pool = [
        e
        for e in entries
        if str(e.get("conflict_key") or "") == key
        and e.get("state") in {"promoted", "contested", "quarantined"}
    ]
    if not pool:
        return None
    promoted = [e for e in pool if e.get("state") == "promoted"]
    if promoted:
        return max(promoted, key=lambda e: authority_score(e)["authority"])
    contested = [e for e in pool if e.get("state") == "contested"]
    if contested:
        return contested[0]
    return pool[0]
