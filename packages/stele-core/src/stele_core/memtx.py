"""MemTX-shaped transactional belief commit (stdlib; write ≠ commit)."""

from __future__ import annotations

import hashlib
import secrets
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps, canonical_loads

TX_DIR = "transactions"
TX_INDEX = "transactions.ndjson"
TX_STATES = frozenset({"open", "validated", "committed", "aborted"})
RISK_TIERS = frozenset({"read", "write", "irreversible"})

# MemTX maturity projection over Stele states
MATURITY = {
    "quarantined": "tentative",
    "contested": "validated",
    "promoted": "action_safe",
    "superseded": "superseded",
    "expired": "superseded",
    "revoked": "revoked",
}


def _tx_dir(root: Path) -> Path:
    return Path(root) / TX_DIR


def _index_path(root: Path) -> Path:
    return Path(root) / TX_INDEX


def _txid() -> str:
    return f"tx_{secrets.token_hex(8)}"


def maturity_of(entry: Mapping[str, Any]) -> str:
    state = str(entry.get("state") or "")
    return MATURITY.get(state, "unknown")


def begin_transaction(
    root: Path,
    *,
    actor: str,
    ts: str,
    risk_tier: str = "write",
    note: str | None = None,
) -> dict[str, Any]:
    """Open a snapshot-isolated staging transaction (MemTX-shaped)."""
    actor = str(actor or "").strip()
    if not actor:
        raise SchemaError("actor is required")
    tier = str(risk_tier or "write").strip().lower()
    if tier not in RISK_TIERS:
        raise SchemaError(f"risk_tier must be one of {sorted(RISK_TIERS)}")
    d = _tx_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    txid = _txid()
    row = {
        "txid": txid,
        "state": "open",
        "actor": actor,
        "ts": ts,
        "risk_tier": tier,
        "staged_ids": [],
        "note": note or "MemTX-shaped belief transaction",
    }
    path = d / f"{txid}.json"
    path.write_text(canonical_dumps(row), encoding="utf-8")
    with _index_path(root).open("a", encoding="utf-8") as fh:
        fh.write(
            canonical_dumps(
                {"txid": txid, "state": "open", "actor": actor, "ts": ts}
            )
            + "\n"
        )
    return dict(row)


def _load_tx(root: Path, txid: str) -> dict[str, Any]:
    path = _tx_dir(root) / f"{txid}.json"
    if not path.is_file():
        raise SchemaError(f"unknown transaction: {txid}")
    return canonical_loads(path.read_text(encoding="utf-8"))


def _save_tx(root: Path, row: dict[str, Any]) -> None:
    path = _tx_dir(root) / f"{row['txid']}.json"
    path.write_text(canonical_dumps(row), encoding="utf-8")


def get_transaction(root: Path, txid: str) -> dict[str, Any]:
    return _load_tx(root, txid)


def list_transactions(
    root: Path, *, state: str | None = None, limit: int = 50
) -> list[dict[str, Any]]:
    if limit < 1:
        raise SchemaError("limit must be >= 1")
    d = _tx_dir(root)
    if not d.is_dir():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(d.glob("tx_*.json"), reverse=True):
        row = canonical_loads(path.read_text(encoding="utf-8"))
        if state and row.get("state") != state:
            continue
        rows.append(row)
        if len(rows) >= limit:
            break
    return rows


def stage_entry(root: Path, txid: str, entry_id: str) -> dict[str, Any]:
    """Attach an existing entry id to an open transaction."""
    entry_id = str(entry_id or "").strip()
    if not entry_id:
        raise SchemaError("entry_id is required")
    row = _load_tx(root, txid)
    if row.get("state") != "open":
        raise SchemaError(f"transaction not open: {row.get('state')}")
    staged = list(row.get("staged_ids") or [])
    if entry_id not in staged:
        staged.append(entry_id)
    row["staged_ids"] = staged
    _save_tx(root, row)
    return dict(row)


def validate_transaction(
    root: Path,
    txid: str,
    entries: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """
    Validate staged beliefs before commit.

    Barriers: missing ids, non-quarantined staged, injection left to caller promote gate.
    """
    row = _load_tx(root, txid)
    if row.get("state") not in {"open", "validated"}:
        raise SchemaError(f"cannot validate transaction in state {row.get('state')}")
    by_id = {str(e.get("id")): e for e in entries}
    barriers: list[str] = []
    staged = list(row.get("staged_ids") or [])
    if not staged:
        barriers.append("empty_stage")
    for eid in staged:
        e = by_id.get(eid)
        if e is None:
            barriers.append(f"missing:{eid}")
            continue
        if e.get("state") != "quarantined":
            barriers.append(f"not_tentative:{eid}:{e.get('state')}")
        if maturity_of(e) != "tentative":
            barriers.append(f"maturity:{eid}:{maturity_of(e)}")
    ok = len(barriers) == 0
    if ok:
        row["state"] = "validated"
        _save_tx(root, row)
    return {
        "ok": ok,
        "txid": txid,
        "barriers": barriers,
        "staged_ids": staged,
        "state": row.get("state"),
        "note": "MemTX validate — tentative only; promote is commit",
    }


def mark_committed(root: Path, txid: str, *, promoted_ids: Sequence[str]) -> dict[str, Any]:
    row = _load_tx(root, txid)
    if row.get("state") not in {"open", "validated"}:
        raise SchemaError(f"cannot commit transaction in state {row.get('state')}")
    row["state"] = "committed"
    row["promoted_ids"] = list(promoted_ids)
    _save_tx(root, row)
    return dict(row)


def mark_aborted(root: Path, txid: str, *, reason: str = "abort") -> dict[str, Any]:
    row = _load_tx(root, txid)
    if row.get("state") in {"committed", "aborted"}:
        raise SchemaError(f"transaction already terminal: {row.get('state')}")
    row["state"] = "aborted"
    row["abort_reason"] = reason
    _save_tx(root, row)
    return dict(row)


def action_safe_gate(
    entries: Iterable[Mapping[str, Any]],
    entry_ids: Sequence[str],
    *,
    open_txs: Sequence[Mapping[str, Any]] | None = None,
    require_action_safe: bool = True,
) -> dict[str, Any]:
    """
    MemTX I1 proxy: irreversible actions require action-safe beliefs.

    Fail-closed if any id is missing, not promoted, or an open tx stages
    the same conflict_key (dirty read of in-flight write).
    """
    by_id = {str(e.get("id")): e for e in entries}
    barriers: list[str] = []
    scores: list[dict[str, Any]] = []
    keys: set[str] = set()
    for eid in entry_ids:
        e = by_id.get(str(eid))
        if e is None:
            barriers.append(f"missing:{eid}")
            continue
        mat = maturity_of(e)
        scores.append({"id": eid, "state": e.get("state"), "maturity": mat})
        if require_action_safe and mat != "action_safe":
            barriers.append(f"not_action_safe:{eid}:{mat}")
        ck = e.get("conflict_key")
        if ck:
            keys.add(str(ck))
    for tx in open_txs or []:
        if tx.get("state") != "open":
            continue
        for eid in tx.get("staged_ids") or []:
            e = by_id.get(str(eid))
            if e is None:
                continue
            ck = e.get("conflict_key")
            if ck and str(ck) in keys:
                barriers.append(
                    f"in_flight_conflict:{tx.get('txid')}:{ck}"
                )
    # Dedupe
    seen: set[str] = set()
    uniq: list[str] = []
    for b in barriers:
        if b not in seen:
            seen.add(b)
            uniq.append(b)
    ok = len(uniq) == 0
    return {
        "ok": ok,
        "allowed": ok,
        "barriers": uniq,
        "scores": scores,
        "note": "MemTX action-safety gate — write is not commit; act only on action_safe",
    }


def aoep_checklist(capabilities: Mapping[str, bool]) -> dict[str, Any]:
    """
    Always-On Evaluation Protocol (AOEP-v0) *shaped* checklist.

    Scores mutation/recovery obligations present — not answer quality.
    """
    required = [
        "transaction_commit",
        "action_safe_gate",
        "cascade_withdraw",
        "version_rollback",
        "forget_or_worth",
    ]
    rows = []
    for key in required:
        rows.append({"obligation": key, "present": bool(capabilities.get(key))})
    score = sum(1 for r in rows if r["present"]) / len(rows)
    return {
        "protocol": "AOEP-v0-shaped",
        "score": round(score, 4),
        "obligations": rows,
        "ok": score >= 1.0,
        "note": "governance obligation coverage — not Always-On paper census",
    }


def tx_digest(row: Mapping[str, Any]) -> str:
    material = {k: v for k, v in row.items() if k != "digest"}
    return hashlib.sha256(canonical_dumps(material).encode("utf-8")).hexdigest()
