"""PoEM-shaped execution ledger + PPMF authority + GPM claim closure (stdlib)."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps, canonical_loads

_GENESIS = "0" * 64
EXECUTIONS_NAME = "executions.ndjson"

ACTION_RISKS = frozenset({"low", "medium", "high", "critical"})
# Minimum authority score required per action risk (PPMF-shaped non-amplification).
RISK_MIN_AUTHORITY: dict[str, float] = {
    "low": 0.0,
    "medium": 0.4,
    "high": 0.7,
    "critical": 0.9,
}


def _exec_path(root: Path) -> Path:
    return Path(root) / EXECUTIONS_NAME


def _row_digest(row: dict[str, Any]) -> str:
    material = {k: v for k, v in row.items() if k != "row_hash"}
    return hashlib.sha256(canonical_dumps(material).encode("utf-8")).hexdigest()


def _iter_rows(root: Path) -> list[dict[str, Any]]:
    path = _exec_path(root)
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(canonical_loads(line))
    return rows


def verify_execution_chain(root: Path) -> dict[str, Any]:
    """Verify append-only execution ledger hash chain (PoEM-shaped)."""
    rows = _iter_rows(root)
    prev = _GENESIS
    for i, row in enumerate(rows):
        if str(row.get("prev_hash") or "") != prev:
            return {
                "ok": False,
                "error": f"prev_hash break at row {i}",
                "row_count": len(rows),
                "head": None,
            }
        expected = _row_digest(row)
        if str(row.get("row_hash") or "") != expected:
            return {
                "ok": False,
                "error": f"row_hash mismatch at row {i}",
                "row_count": len(rows),
                "head": None,
            }
        prev = expected
    return {
        "ok": True,
        "row_count": len(rows),
        "head": prev if rows else _GENESIS,
        "note": "execution chain — independent of memory entry bodies (PoEM-shaped)",
    }


def record_execution(
    root: Path,
    *,
    step: str,
    subject_id: str,
    actor: str,
    ts: str,
    detail: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Append a proof-of-execution row. Only trusted caller code should invoke this.

    Does not inspect or trust memory entry wording — PoEM thesis.
    """
    step = str(step or "").strip()
    subject_id = str(subject_id or "").strip()
    actor = str(actor or "").strip()
    if not step or not subject_id or not actor:
        raise SchemaError("step, subject_id, and actor are required")
    chain = verify_execution_chain(root)
    if not chain.get("ok"):
        raise SchemaError(f"execution chain broken: {chain.get('error')}")
    prev = str(chain.get("head") or _GENESIS)
    detail_obj = dict(detail or {})
    detail_digest = hashlib.sha256(
        canonical_dumps(detail_obj).encode("utf-8")
    ).hexdigest()
    row: dict[str, Any] = {
        "step": step,
        "subject_id": subject_id,
        "actor": actor,
        "ts": ts,
        "detail_digest": detail_digest,
        "prev_hash": prev,
    }
    row["row_hash"] = _row_digest(row)
    path = _exec_path(root)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(canonical_dumps(row) + "\n")
    return {
        "ok": True,
        "row": row,
        "head": row["row_hash"],
        "note": "recorded execution — not a memory entry body claim",
    }


def verify_execution_claim(
    root: Path,
    *,
    step: str,
    subject_id: str,
) -> dict[str, Any]:
    """
    Allow skipping a safety step only if the execution ledger confirms it ran.

    Ignores memory entry text entirely (PoEM vs wording-based defenses).
    """
    step = str(step or "").strip()
    subject_id = str(subject_id or "").strip()
    if not step or not subject_id:
        raise SchemaError("step and subject_id are required")
    chain = verify_execution_chain(root)
    if not chain.get("ok"):
        return {
            "ok": False,
            "allowed": False,
            "matched": None,
            "reason": f"chain_broken:{chain.get('error')}",
            "note": "fail-closed — do not skip safety step",
        }
    matches = [
        r
        for r in _iter_rows(root)
        if str(r.get("step") or "") == step
        and str(r.get("subject_id") or "") == subject_id
    ]
    if not matches:
        return {
            "ok": True,
            "allowed": False,
            "matched": None,
            "reason": "no_execution_row",
            "note": "fail-closed — memory claims alone never authorize skip",
        }
    # Cross-subject replay defense: subject_id must match exactly (already filtered).
    latest = matches[-1]
    return {
        "ok": True,
        "allowed": True,
        "matched": {
            "step": latest.get("step"),
            "subject_id": latest.get("subject_id"),
            "ts": latest.get("ts"),
            "actor": latest.get("actor"),
            "row_hash": latest.get("row_hash"),
        },
        "reason": "execution_confirmed",
        "note": "skip allowed only because ledger confirms execution (PoEM-shaped)",
    }


def list_executions(
    root: Path, *, subject_id: str | None = None, limit: int = 50
) -> list[dict[str, Any]]:
    if limit < 1:
        raise SchemaError("limit must be >= 1")
    rows = _iter_rows(root)
    if subject_id is not None:
        sid = str(subject_id).strip()
        rows = [r for r in rows if str(r.get("subject_id") or "") == sid]
    return rows[-limit:]


def authority_score(entry: Mapping[str, Any]) -> dict[str, Any]:
    """
    Deterministic authority score from platform-maintained provenance (PPMF-shaped).

    Caps pack-hydrate / unknown sources so consolidation cannot launder authority.
    """
    state = str(entry.get("state") or "")
    prov = entry.get("provenance") or {}
    agent = str(prov.get("agent") or "")
    source = str(prov.get("source") or "")
    reasons: list[str] = []
    score = 0.3
    if state == "promoted":
        score = 0.5
        reasons.append("promoted")
    elif state in {"contested", "revoked", "quarantine"}:
        score = 0.1
        reasons.append(f"state={state}")
    if agent == "pack-hydrate":
        score = min(score, 0.25)
        reasons.append("pack_hydrate_cap")
    if agent in {"migration", "oracle"}:
        score = max(score, 0.75)
        reasons.append(f"agent={agent}")
    if source.startswith("oracle:") or source.startswith("ci:"):
        score = max(score, 0.85)
        reasons.append("trusted_source_prefix")
    elif source.startswith("session:"):
        score = max(score, 0.45)
        reasons.append("session_source")
    elif source.startswith("pack:"):
        score = min(score, 0.3)
        reasons.append("pack_source_cap")
    if entry.get("evidence"):
        score = min(1.0, score + 0.1)
        reasons.append("has_evidence")
    return {
        "id": entry.get("id"),
        "authority": round(score, 4),
        "reasons": reasons,
        "agent": agent,
        "source": source,
        "state": state,
    }


def authority_gate(
    entries: Iterable[Mapping[str, Any]],
    entry_ids: Sequence[str],
    *,
    action_risk: str,
) -> dict[str, Any]:
    """
    Non-amplification firewall: action risk must not exceed max memory authority.

    PPMF-shaped — uses platform provenance, not LLM-rewritten body claims.
    """
    risk = str(action_risk or "").strip().lower()
    if risk not in ACTION_RISKS:
        raise SchemaError(f"action_risk must be one of {sorted(ACTION_RISKS)}")
    by_id = {str(e.get("id")): e for e in entries}
    missing = [i for i in entry_ids if i not in by_id]
    if missing:
        return {
            "ok": False,
            "allowed": False,
            "action_risk": risk,
            "required_authority": RISK_MIN_AUTHORITY[risk],
            "max_authority": 0.0,
            "missing_ids": missing,
            "scores": [],
            "note": "fail-closed — unknown memories cannot authorize",
        }
    scores = [authority_score(by_id[i]) for i in entry_ids]
    max_auth = max((s["authority"] for s in scores), default=0.0)
    required = RISK_MIN_AUTHORITY[risk]
    allowed = max_auth >= required
    return {
        "ok": True,
        "allowed": allowed,
        "action_risk": risk,
        "required_authority": required,
        "max_authority": max_auth,
        "missing_ids": [],
        "scores": scores,
        "note": "PPMF-shaped non-amplification — provenance caps pack/session authority",
    }


def claim_closure(
    entries: Iterable[Mapping[str, Any]],
    claim_ids: Sequence[str],
    *,
    journal_head: str | None = None,
    expected_head: str | None = None,
) -> dict[str, Any]:
    """
    GPM-shaped exact claim closure over a fresh public view.

    Every claim_id must be an assertable promoted fact (not contested/revoked).
    Head mismatch → fail closed.
    """
    if not claim_ids:
        raise SchemaError("claim_ids must be non-empty")
    if expected_head is not None and expected_head != journal_head:
        return {
            "ok": False,
            "closed": False,
            "barriers": ["head_mismatch"],
            "claims": [],
            "head": journal_head,
            "note": "fail-closed claim closure (GPM-shaped)",
        }
    by_id = {str(e.get("id")): e for e in entries}
    claims: list[dict[str, Any]] = []
    barriers: list[str] = []
    for cid in claim_ids:
        e = by_id.get(str(cid))
        if e is None:
            barriers.append(f"missing:{cid}")
            claims.append({"id": cid, "assertable": False, "reason": "missing"})
            continue
        state = str(e.get("state") or "")
        if state != "promoted":
            barriers.append(f"not_promoted:{cid}:{state}")
            claims.append({"id": cid, "assertable": False, "reason": f"state={state}"})
            continue
        claims.append({"id": cid, "assertable": True, "reason": "promoted", "title": e.get("title")})
    closed = len(barriers) == 0
    return {
        "ok": closed,
        "closed": closed,
        "barriers": barriers,
        "claims": claims,
        "head": journal_head,
        "note": "exact claim closure over promoted facts — not free-text entailment",
    }
