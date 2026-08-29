"""Store integrity checks (C4) — SoT inspectable and consistent.

Checks are backend-agnostic: they use ``store_id``, ``iter_entries``, and
``iter_journal``. File-layout dual-location (quarantine + promoted) is checked
only when the store exposes ``entries_q`` / ``entries_p`` Path dirs.
"""

from __future__ import annotations

import hashlib
from typing import Any, Protocol, runtime_checkable

from stele_core.schema import SchemaError, canonical_dumps, canonical_loads, validate_entry


@runtime_checkable
class StoreLike(Protocol):
    """Minimal store surface for integrity / doctor (file or MySQL)."""

    @property
    def store_id(self) -> str: ...

    def iter_entries(self, *, states: Any = None): ...

    def iter_journal(self, *, entry_id: str | None = None): ...

    def read_entry(self, entry_id: str) -> dict[str, Any] | None: ...

# Belief-content keys for MemMark-shaped content digests (exclude volatile usage counters).
_DIGEST_KEYS = (
    "id",
    "layer",
    "title",
    "body",
    "scope",
    "state",
    "temporal",
    "provenance",
    "env_assumptions",
    "links",
    "evidence",
    "contested_with",
    "assessment",
    "conflict_key",
    "cue_tags",
)


def entry_content_digest(entry: dict[str, Any]) -> str:
    """SHA-256 of canonical belief content (MemMark snapshot attribution carrier)."""
    payload = {k: entry.get(k) for k in _DIGEST_KEYS if k in entry}
    blob = canonical_dumps(payload).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def journal_digest(store: StoreLike) -> str:
    """SHA-256 over journal content (file bytes when present; else row JSON)."""
    journal_path = getattr(store, "journal_path", None)
    if journal_path is not None and hasattr(journal_path, "exists"):
        if not journal_path.exists():
            return hashlib.sha256(b"").hexdigest()
        return hashlib.sha256(journal_path.read_bytes()).hexdigest()
    # Non-file backends (MySQL): hash canonical NDJSON of iter_journal rows.
    parts = [canonical_dumps(row).encode("utf-8") for row in store.iter_journal()]
    blob = b"\n".join(parts) + (b"\n" if parts else b"")
    return hashlib.sha256(blob).hexdigest()


_GENESIS = "0" * 64


def _journal_row_digest(row: dict[str, Any]) -> str:
    material = {k: v for k, v in row.items() if k != "row_hash"}
    return hashlib.sha256(canonical_dumps(material).encode("utf-8")).hexdigest()


def verify_journal_chain(store: StoreLike) -> dict[str, Any]:
    """
    GPM-shaped journal hash-chain verification (fail-closed report).

    Legacy rows without prev_hash/row_hash are accepted as a soft prefix
    (derived digests only). Chained rows must match prev_hash → row_hash.
    """
    rows = list(store.iter_journal())
    breaks: list[dict[str, Any]] = []
    prev = _GENESIS
    chained = 0
    legacy = 0
    head = _GENESIS
    for i, row in enumerate(rows):
        if "row_hash" in row and "prev_hash" in row:
            chained += 1
            expected_prev = str(row.get("prev_hash") or "")
            if expected_prev != prev and not (i == 0 and expected_prev == _GENESIS and prev == _GENESIS):
                # First chained row after legacy prefix may start a new chain
                if legacy and expected_prev == _GENESIS:
                    prev = _GENESIS
                elif expected_prev != prev:
                    breaks.append(
                        {
                            "index": i,
                            "op": row.get("op"),
                            "entry_id": row.get("entry_id"),
                            "reason": "prev_hash_mismatch",
                            "expected_prev": prev,
                            "got_prev": expected_prev,
                        }
                    )
            digest = _journal_row_digest(row)
            got = str(row.get("row_hash") or "")
            if got != digest:
                breaks.append(
                    {
                        "index": i,
                        "op": row.get("op"),
                        "entry_id": row.get("entry_id"),
                        "reason": "row_hash_mismatch",
                    }
                )
            prev = got if got else digest
            head = prev
        else:
            legacy += 1
            # Derived link for soft continuity
            digest = _journal_row_digest(row)
            prev = digest
            head = digest
    return {
        "ok": len(breaks) == 0,
        "row_count": len(rows),
        "chained_rows": chained,
        "legacy_rows": legacy,
        "head": head,
        "breaks": breaks,
        "note": "GPM-shaped journal chain — not distributed consensus",
    }


def journal_chain_head(store: StoreLike) -> dict[str, Any]:
    """Return current journal chain head + counts."""
    report = verify_journal_chain(store)
    return {
        "head": report["head"],
        "row_count": report["row_count"],
        "chained_rows": report["chained_rows"],
        "legacy_rows": report["legacy_rows"],
        "ok": report["ok"],
    }


def store_seal(store: StoreLike) -> dict[str, Any]:
    """
    Tamper-evident seal over entry content digests + journal (Merkle-flat root).

    Not a full Merkle tree — sorted (id, digest) pairs hashed with journal digest.
    Survives as a snapshot attestation (MemMark R3-adjacent).
    """
    pairs: list[tuple[str, str]] = []
    for e in store.iter_entries():
        pairs.append((e["id"], entry_content_digest(e)))
    pairs.sort(key=lambda x: x[0])
    jdig = journal_digest(store)
    material = canonical_dumps({"entries": pairs, "journal_digest": jdig}).encode("utf-8")
    root = hashlib.sha256(material).hexdigest()
    return {
        "algorithm": "sha256",
        "root": root,
        "entry_count": len(pairs),
        "journal_digest": jdig,
        "entries": [{"id": i, "content_digest": d} for i, d in pairs],
        "note": "flat content seal — not TRACE behavioral watermark",
    }


def verify_seal(store: StoreLike, seal: dict[str, Any]) -> dict[str, Any]:
    """Compare a prior seal to the live store."""
    live = store_seal(store)
    expected = str(seal.get("root") or "")
    ok = bool(expected) and expected == live["root"]
    return {
        "ok": ok,
        "expected_root": expected or None,
        "live_root": live["root"],
        "entry_count_live": live["entry_count"],
        "entry_count_seal": seal.get("entry_count"),
        "journal_digest_live": live["journal_digest"],
        "journal_digest_seal": seal.get("journal_digest"),
    }


def attribution_receipt(store: StoreLike, entry_id: str) -> dict[str, Any]:
    """
    Snapshot-usable attribution receipt for one entry (MemMark R3-shaped).

    Binds content digest + journal ops + link refs. No secret-keyed sampler (C5).
    """
    entry = store.read_entry(entry_id)
    journal = [
        {"op": r["op"], "actor": r["actor"], "ts": r["ts"]}
        for r in store.iter_journal(entry_id=entry_id)
    ]
    if entry is None and not journal:
        raise SchemaError(f"unknown entry: {entry_id}")
    digest = entry_content_digest(entry) if entry else None
    return {
        "id": entry_id,
        "present": entry is not None,
        "content_digest": digest,
        "state": (entry or {}).get("state"),
        "title": (entry or {}).get("title"),
        "links": list((entry or {}).get("links") or [])[:16],
        "superseded_by": ((entry or {}).get("temporal") or {}).get("superseded_by"),
        "journal": journal,
        "note": "deterministic receipt — not MemMark keyed watermark",
    }


def replay_consistency(store: StoreLike) -> dict[str, Any]:
    """
    Soft journal↔SoT consistency checks (TOKI replay-adjacent; no LLM).

    Flags: journal ADD without live entry and without later DELETE;
    live entries with zero journal rows (warn).
    """
    live_ids = {e["id"] for e in store.iter_entries()}
    added: set[str] = set()
    deleted: set[str] = set()
    for row in store.iter_journal():
        eid = row.get("entry_id")
        op = str(row.get("op") or "")
        if op == "ADD" and eid:
            added.add(str(eid))
        elif op == "DELETE" and eid:
            deleted.add(str(eid))
        elif op == "PURGE":
            if eid:
                deleted.add(str(eid))
            for rid in row.get("removed") or []:
                deleted.add(str(rid))
            payload = row.get("payload") or {}
            for rid in payload.get("removed") or []:
                deleted.add(str(rid))

    missing_after_add = sorted((added - deleted) - live_ids)
    live_without_journal = sorted(live_ids - added)
    return {
        "ok": len(missing_after_add) == 0,
        "missing_after_add": missing_after_add,
        "live_without_journal": live_without_journal,
        "added_count": len(added),
        "live_count": len(live_ids),
        "note": "soft replay check — journal ADD must resolve to live or DELETE/PURGE",
    }


def verify_store(store: StoreLike) -> dict[str, Any]:
    """
    Read-only integrity report. Does not mutate the store.

    Checks: store_id present, entries schema-valid, no dual-location ids
    (file layout only), journal rows parseable via ``iter_journal``.
    Indexes are derived — absence is not an error.
    """
    errors: list[str] = []
    warnings: list[str] = []
    entry_count = 0
    ids: set[str] = set()

    try:
        sid = store.store_id
        if not sid:
            errors.append("store_id missing or empty")
    except Exception as exc:  # noqa: BLE001 — surface backend failures
        errors.append(f"store_id unreadable: {exc}")

    manifest_path = getattr(store, "manifest_path", None)
    if manifest_path is not None and hasattr(manifest_path, "exists"):
        if not manifest_path.exists():
            errors.append("missing stele.json manifest")
        else:
            try:
                manifest = canonical_loads(manifest_path.read_text(encoding="utf-8"))
                if "store_id" not in manifest:
                    errors.append("manifest missing store_id")
            except Exception as exc:  # noqa: BLE001 — surface parse failures
                errors.append(f"manifest unreadable: {exc}")

    entries_q = getattr(store, "entries_q", None)
    entries_p = getattr(store, "entries_p", None)
    if (
        entries_q is not None
        and entries_p is not None
        and hasattr(entries_q, "glob")
        and hasattr(entries_p, "glob")
    ):
        q_ids = {p.stem for p in entries_q.glob("*.json")}
        p_ids = {p.stem for p in entries_p.glob("*.json")}
        dual = q_ids & p_ids
        if dual:
            errors.append(f"entries present in quarantine and promoted: {sorted(dual)}")

    for entry in store.iter_entries():
        entry_count += 1
        eid = entry.get("id")
        if not eid:
            errors.append("entry missing id")
            continue
        if eid in ids:
            errors.append(f"duplicate entry id: {eid}")
        ids.add(eid)
        try:
            validate_entry(entry, allow_state=entry.get("state"))
        except SchemaError as exc:
            errors.append(f"{eid}: {exc}")

    journal_lines = 0
    journal_path = getattr(store, "journal_path", None)
    if journal_path is not None and hasattr(journal_path, "exists"):
        if journal_path.exists():
            for line in journal_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                journal_lines += 1
                try:
                    canonical_loads(line)
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"journal line unreadable: {exc}")
                    break
        else:
            warnings.append("missing journal.ndjson")
    else:
        for row in store.iter_journal():
            journal_lines += 1
            if not isinstance(row, dict):
                errors.append("journal row is not an object")
                break

    return {
        "ok": len(errors) == 0,
        "entry_count": entry_count,
        "journal_lines": journal_lines,
        "errors": errors,
        "warnings": warnings,
    }
