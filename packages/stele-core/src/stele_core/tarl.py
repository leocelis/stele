"""TARL-shaped five-action memory update classify + apply (stdlib; no LLM)."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from stele_core.execution import authority_score
from stele_core.index.lexical import tokenize
from stele_core.risk import scan_text
from stele_core.schema import SchemaError, canonical_dumps

TARL_ACTIONS = frozenset(
    {"append", "noop", "revise", "reject_conflict", "defer_verify"}
)


def _body_digest(entry: Mapping[str, Any]) -> str:
    material = {
        "title": str(entry.get("title") or "").strip().lower(),
        "body": str(entry.get("body") or "").strip().lower(),
    }
    return hashlib.sha256(canonical_dumps(material).encode("utf-8")).hexdigest()


def _jaccard(a: Mapping[str, Any], b: Mapping[str, Any]) -> float:
    ta = set(tokenize(f"{a.get('title') or ''} {a.get('body') or ''}"))
    tb = set(tokenize(f"{b.get('title') or ''} {b.get('body') or ''}"))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _active_by_key(
    entries: Iterable[Mapping[str, Any]], conflict_key: str
) -> list[dict[str, Any]]:
    key = str(conflict_key)
    out: list[dict[str, Any]] = []
    for e in entries:
        if str(e.get("conflict_key") or "") != key:
            continue
        if e.get("state") in {"promoted", "contested"}:
            out.append(dict(e))
    return out


def classify_update(
    candidate: Mapping[str, Any],
    entries: Sequence[Mapping[str, Any]],
    *,
    revise_jaccard: float = 0.15,
) -> dict[str, Any]:
    """
    Deterministic TARL action for an incoming statement.

    Actions: append | noop | revise | reject_conflict | defer_verify.
    No LLM — conflict_key + body digest + authority + injection markers.
    """
    if revise_jaccard < 0 or revise_jaccard > 1:
        raise SchemaError("revise_jaccard must be in [0, 1]")
    text = f"{candidate.get('title') or ''}\n{candidate.get('body') or ''}"
    markers = scan_text(text)
    if markers:
        return {
            "action": "reject_conflict",
            "target_id": None,
            "reasons": [f"injection_markers:{','.join(markers)}"],
            "note": "TARL-shaped — injection never enters accepted ledger",
        }

    key = candidate.get("conflict_key")
    if not key:
        return {
            "action": "append",
            "target_id": None,
            "reasons": ["no_conflict_key"],
            "note": "TARL-shaped append — new slot",
        }

    actives = _active_by_key(entries, str(key))
    if not actives:
        return {
            "action": "append",
            "target_id": None,
            "reasons": [f"no_active_for_key:{key}"],
            "note": "TARL-shaped append — first assertion for key",
        }

    promoted = [e for e in actives if e.get("state") == "promoted"]
    pool = promoted or actives
    pool.sort(
        key=lambda e: str((e.get("temporal") or {}).get("last_verified") or ""),
        reverse=True,
    )
    target = pool[0]

    if _body_digest(candidate) == _body_digest(target):
        return {
            "action": "noop",
            "target_id": target.get("id"),
            "reasons": ["exact_body_digest_match"],
            "note": "TARL-shaped noop — duplicate assertion",
        }

    cand_auth = authority_score(
        {
            **dict(candidate),
            "state": candidate.get("state") or "quarantined",
            "id": candidate.get("id") or "candidate",
        }
    )["authority"]
    tgt_auth = authority_score(target)["authority"]
    overlap = _jaccard(candidate, target)
    reasons = [
        f"cand_auth={cand_auth}",
        f"tgt_auth={tgt_auth}",
        f"jaccard={round(overlap, 4)}",
    ]

    if cand_auth + 1e-9 < tgt_auth - 0.15:
        return {
            "action": "reject_conflict",
            "target_id": target.get("id"),
            "reasons": reasons + ["weaker_source"],
            "note": "TARL-shaped reject — weaker authority than active",
        }

    if abs(cand_auth - tgt_auth) <= 0.05 and overlap < revise_jaccard:
        return {
            "action": "defer_verify",
            "target_id": target.get("id"),
            "reasons": reasons + ["authority_tie_low_overlap"],
            "note": "TARL-shaped defer — pending ledger until evidence",
        }

    if cand_auth >= tgt_auth - 0.15:
        return {
            "action": "revise",
            "target_id": target.get("id"),
            "reasons": reasons + ["authority_within_revise_band"],
            "note": "TARL-shaped revise — supersede active under key",
        }

    return {
        "action": "defer_verify",
        "target_id": target.get("id"),
        "reasons": reasons + ["fallback_defer"],
        "note": "TARL-shaped defer — ambiguous update",
    }


def ledger_view(entries: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Map Stele states → TARL accepted / pending / rejected ledgers."""
    accepted: list[str] = []
    pending: list[str] = []
    rejected: list[str] = []
    for e in entries:
        eid = str(e.get("id") or "")
        state = str(e.get("state") or "")
        if state == "promoted":
            accepted.append(eid)
        elif state == "quarantined":
            pending.append(eid)
        elif state in {"revoked", "superseded", "expired"}:
            rejected.append(eid)
        elif state == "contested":
            pending.append(eid)  # unresolved → pending
    return {
        "accepted": sorted(accepted),
        "pending": sorted(pending),
        "rejected": sorted(rejected),
        "counts": {
            "accepted": len(accepted),
            "pending": len(pending),
            "rejected": len(rejected),
        },
        "note": "TARL-shaped ledger projection over Stele states",
    }
