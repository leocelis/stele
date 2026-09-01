"""File-backed store: SoT entries, append-only journal, advisory lock (C4, C5)."""

from __future__ import annotations

import hashlib
import os
import time
import uuid
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps, canonical_loads, validate_entry

MANIFEST_NAME = "stele.json"
JOURNAL_NAME = "journal.ndjson"
LOCK_NAME = ".lock"
_GENESIS_HASH = "0" * 64


def _row_content_digest(row: dict[str, Any]) -> str:
    """SHA-256 of journal row excluding row_hash (chain carrier)."""
    material = {k: v for k, v in row.items() if k != "row_hash"}
    return hashlib.sha256(canonical_dumps(material).encode("utf-8")).hexdigest()


class StoreError(RuntimeError):
    """Store I/O or locking failure."""


class SteleStore:
    """Inspectable file SoT. Indexes under index/ are derived and rebuildable."""

    backend = "file"

    def __init__(self, root: Path, *, store_id: str | None = None, create: bool = True):
        self.root = Path(root)
        self.entries_q = self.root / "entries" / "quarantine"
        self.entries_p = self.root / "entries" / "promoted"
        self.attachments = self.root / "attachments"
        self.index_dir = self.root / "index"
        self.journal_path = self.root / JOURNAL_NAME
        self.manifest_path = self.root / MANIFEST_NAME
        self.lock_path = self.root / LOCK_NAME
        if create:
            self._ensure_layout(store_id=store_id)
        elif not self.manifest_path.exists():
            raise StoreError(f"no stele store at {self.root}")

    def _ensure_layout(self, *, store_id: str | None) -> None:
        for d in (
            self.entries_q,
            self.entries_p,
            self.attachments,
            self.index_dir / "lexical",
            self.index_dir / "semantic",
            self.index_dir / "temporal",
        ):
            d.mkdir(parents=True, exist_ok=True)
        if not self.manifest_path.exists():
            manifest = {
                "schema_version": 1,
                "store_id": store_id or f"store_{uuid.uuid4().hex[:12]}",
                "created_at": _caller_or_placeholder_ts(),
            }
            self._atomic_write_text(self.manifest_path, canonical_dumps(manifest))
        if not self.journal_path.exists():
            self.journal_path.touch()

    @property
    def store_id(self) -> str:
        return canonical_loads(self.manifest_path.read_text(encoding="utf-8"))["store_id"]

    # ----- locking ---------------------------------------------------------

    def acquire(self, *, timeout_s: float = 10.0) -> None:
        deadline = time.monotonic() + timeout_s
        while True:
            try:
                fd = os.open(str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                return
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise StoreError(f"could not acquire lock at {self.lock_path}")
                time.sleep(0.01)

    def release(self) -> None:
        try:
            self.lock_path.unlink(missing_ok=True)  # type: ignore[call-arg]
        except TypeError:
            if self.lock_path.exists():
                self.lock_path.unlink()

    def __enter__(self) -> SteleStore:
        self.acquire()
        return self

    def __exit__(self, *exc: object) -> None:
        self.release()

    # ----- paths -----------------------------------------------------------

    def _path_for(self, entry_id: str, state: str) -> Path:
        folder = self.entries_q if state == "quarantined" else self.entries_p
        # promoted folder also holds superseded/expired/contested (still on disk)
        if state != "quarantined":
            folder = self.entries_p
        return folder / f"{entry_id}.json"

    def _find_path(self, entry_id: str) -> Path | None:
        for folder in (self.entries_q, self.entries_p):
            p = folder / f"{entry_id}.json"
            if p.exists():
                return p
        return None

    # ----- journal ---------------------------------------------------------

    def journal(
        self,
        op: str,
        *,
        entry_id: str | None = None,
        actor: str,
        payload: dict[str, Any] | None = None,
        ts: str,
    ) -> None:
        # GPM-shaped hash chain: bind each row to the previous row_hash (or genesis).
        prev_hash = _GENESIS_HASH
        if self.journal_path.exists() and self.journal_path.stat().st_size > 0:
            last = ""
            with self.journal_path.open("r", encoding="utf-8") as fh:
                for last in fh:
                    pass
            if last.strip():
                try:
                    prev_row = canonical_loads(last)
                    prev_hash = str(prev_row.get("row_hash") or _row_content_digest(prev_row))
                except Exception:  # noqa: BLE001 — fall back to genesis on corrupt last line
                    prev_hash = _GENESIS_HASH
        line: dict[str, Any] = {
            "op": op,
            "entry_id": entry_id,
            "actor": actor,
            "ts": ts,
            "payload_digest": None,
            "prev_hash": prev_hash,
        }
        if payload is not None:
            line["payload_digest"] = hashlib.sha256(
                canonical_dumps(payload).encode("utf-8")
            ).hexdigest()
            # Retain lightweight purge id list for replay_consistency (not full payload).
            if op == "PURGE" and isinstance(payload.get("removed"), list):
                line["removed"] = [str(x) for x in payload["removed"]]
        line["row_hash"] = _row_content_digest(line)
        with self.journal_path.open("a", encoding="utf-8") as fh:
            fh.write(canonical_dumps(line).rstrip("\n") + "\n")

    def iter_journal(self, *, entry_id: str | None = None) -> Iterator[dict[str, Any]]:
        """Yield journal rows (optionally filtered to one entry)."""
        if not self.journal_path.exists():
            return
        for line in self.journal_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = canonical_loads(line)
            if entry_id is not None and row.get("entry_id") != entry_id:
                continue
            yield row

    # ----- CRUD helpers ----------------------------------------------------

    def write_entry(self, entry: dict[str, Any], *, actor: str, ts: str, op: str) -> dict[str, Any]:
        validated = validate_entry(entry, allow_state=entry.get("state"))
        state = validated["state"]
        path = self._path_for(validated["id"], state)
        # remove any prior location (state transition)
        old = self._find_path(validated["id"])
        self._atomic_write_text(path, canonical_dumps(validated))
        if old is not None and old.resolve() != path.resolve():
            old.unlink()
        self.journal(op, entry_id=validated["id"], actor=actor, payload=validated, ts=ts)
        return validated

    def read_entry(self, entry_id: str) -> dict[str, Any] | None:
        path = self._find_path(entry_id)
        if path is None:
            return None
        return canonical_loads(path.read_text(encoding="utf-8"))

    def delete_entry_file(self, entry_id: str, *, actor: str, ts: str, reason: str) -> bool:
        path = self._find_path(entry_id)
        if path is None:
            return False
        path.unlink()
        self.journal(
            "DELETE",
            entry_id=entry_id,
            actor=actor,
            payload={"reason": reason},
            ts=ts,
        )
        return True

    def iter_entries(self, *, states: Iterable[str] | None = None) -> Iterator[dict[str, Any]]:
        want = set(states) if states is not None else None
        for folder in (self.entries_q, self.entries_p):
            for path in sorted(folder.glob("*.json")):
                entry = canonical_loads(path.read_text(encoding="utf-8"))
                if want is None or entry.get("state") in want:
                    yield entry

    def drop_indexes(self) -> None:
        for sub in ("lexical", "semantic", "temporal"):
            d = self.index_dir / sub
            if d.exists():
                for child in d.iterdir():
                    if child.is_file():
                        child.unlink()

    def put_attachment(self, data: bytes) -> str:
        digest = hashlib.sha256(data).hexdigest()
        path = self.attachments / digest
        if not path.exists():
            path.write_bytes(data)
        return digest

    def verify_attachment_digest(self, digest: str) -> bool:
        path = self.attachments / digest
        if not path.exists():
            return False
        return hashlib.sha256(path.read_bytes()).hexdigest() == digest

    @staticmethod
    def _atomic_write_text(path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)


def _caller_or_placeholder_ts() -> str:
    # Manifest creation only; ops require caller-supplied timestamps (C5 determinism).
    return "1970-01-01T00:00:00Z"


def require_ts(ts: str | None, field: str = "ts") -> str:
    if not ts:
        raise SchemaError(f"{field} is required (caller-supplied; store never reads the clock)")
    return ts
