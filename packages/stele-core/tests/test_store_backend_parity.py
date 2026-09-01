"""Regression: integrity/doctor must work without file-layout attributes.

Hosted MySQLSteleStore has no ``manifest_path`` / ``journal_path`` / ``entries_*``.
``stele_doctor`` previously crashed with AttributeError on that path.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

import pytest

from stele_core.integrity import (
    journal_digest,
    replay_consistency,
    store_seal,
    verify_journal_chain,
    verify_store,
)
from stele_core.mysql_store import MySQLSteleStore
from stele_core.ops import Stele
from stele_core.schema import SchemaError
from stele_core.store import SteleStore

TS = "2026-08-29T15:00:00Z"

# Surface every ops path that doctor / health_report touch on the store.
_REQUIRED_STORE_METHODS = (
    "iter_entries",
    "iter_journal",
    "read_entry",
    "write_entry",
    "delete_entry_file",
    "journal",
    "acquire",
    "release",
    "put_attachment",
    "verify_attachment_digest",
    "drop_indexes",
)


class _MemoryStore:
    """Minimal non-file store — deliberately lacks manifest_path / journal_path."""

    backend = "memory"

    def __init__(self, store_id: str = "mem_parity") -> None:
        self.root = Path("/tmp/stele-memory-unused")  # noqa: S108 — unused sentinel
        self.index_dir = self.root / "index"
        self.attachments = self.root / "attachments"
        self._store_id = store_id
        self._entries: dict[str, dict[str, Any]] = {}
        self._journal: list[dict[str, Any]] = []

    @property
    def store_id(self) -> str:
        return self._store_id

    def acquire(self, *, timeout_s: float = 10.0) -> None:
        return None

    def release(self) -> None:
        return None

    def __enter__(self) -> _MemoryStore:
        self.acquire()
        return self

    def __exit__(self, *exc: object) -> None:
        self.release()

    def journal(
        self,
        op: str,
        *,
        entry_id: str | None = None,
        actor: str,
        payload: dict[str, Any] | None = None,
        ts: str,
    ) -> None:
        self._journal.append(
            {
                "op": op,
                "entry_id": entry_id,
                "actor": actor,
                "ts": ts,
                "payload": payload,
            }
        )

    def iter_journal(self, *, entry_id: str | None = None) -> Iterator[dict[str, Any]]:
        for row in self._journal:
            if entry_id is None or row.get("entry_id") == entry_id:
                yield dict(row)

    def write_entry(self, entry: dict[str, Any], *, actor: str, ts: str, op: str) -> dict[str, Any]:
        from stele_core.schema import validate_entry

        validated = validate_entry(entry, allow_state=entry.get("state"))
        self._entries[validated["id"]] = validated
        self.journal(op, entry_id=validated["id"], actor=actor, payload=validated, ts=ts)
        return validated

    def read_entry(self, entry_id: str) -> dict[str, Any] | None:
        return self._entries.get(entry_id)

    def delete_entry_file(self, entry_id: str, *, actor: str, ts: str, reason: str) -> bool:
        if entry_id not in self._entries:
            return False
        del self._entries[entry_id]
        self.journal("DELETE", entry_id=entry_id, actor=actor, payload={"reason": reason}, ts=ts)
        return True

    def iter_entries(self, *, states: Iterable[str] | None = None) -> Iterator[dict[str, Any]]:
        want = set(states) if states is not None else None
        for entry in self._entries.values():
            if want is None or entry.get("state") in want:
                yield entry

    def drop_indexes(self) -> None:
        return None

    def put_attachment(self, data: bytes) -> str:
        import hashlib

        return hashlib.sha256(data).hexdigest()

    def verify_attachment_digest(self, digest: str) -> bool:
        return False


def test_memory_store_lacks_file_layout_attrs() -> None:
    store = _MemoryStore()
    assert not hasattr(store, "manifest_path")
    assert not hasattr(store, "journal_path")
    assert not hasattr(store, "entries_q")
    assert not hasattr(store, "entries_p")


def test_verify_store_and_doctor_without_manifest_path() -> None:
    """Regression for hosted doctor: AttributeError on missing manifest_path."""
    store = _MemoryStore(store_id="parity_doc")
    assert not hasattr(store, "manifest_path")

    report = verify_store(store)
    assert report["ok"] is True
    assert report["entry_count"] == 0
    assert report["errors"] == []

    assert isinstance(journal_digest(store), str)
    assert verify_journal_chain(store)["ok"] is True
    assert store_seal(store)["entry_count"] == 0
    assert replay_consistency(store)["ok"] is True

    stele = Stele(store, now=TS)
    doc = stele.doctor(now=TS)
    assert doc["ok"] is True
    assert doc["verify"]["ok"] is True
    assert doc["stats"]["total"] == 0
    assert doc["contested_ids"] == []
    assert doc["stale_ids"] == []


def test_mysql_store_class_exposes_required_surface_without_file_attrs() -> None:
    """Static parity — MySQL class must implement ops surface, not file layout."""
    for name in _REQUIRED_STORE_METHODS:
        assert hasattr(MySQLSteleStore, name), f"MySQLSteleStore missing {name}"
    assert isinstance(MySQLSteleStore.store_id, property)
    assert MySQLSteleStore.backend == "mysql"
    assert not hasattr(MySQLSteleStore, "manifest_path")
    assert not hasattr(MySQLSteleStore, "journal_path")
    assert not hasattr(MySQLSteleStore, "entries_q")
    assert not hasattr(MySQLSteleStore, "entries_p")


def test_file_store_still_has_layout_attrs(tmp_path: Path) -> None:
    store = SteleStore(tmp_path / "s", store_id="file_parity", create=True)
    assert store.backend == "file"
    assert store.manifest_path.exists()
    assert store.journal_path.exists()
    assert store.entries_q.is_dir()
    report = verify_store(store)
    assert report["ok"] is True
    stele = Stele(store, now=TS)
    assert stele.doctor(now=TS)["ok"] is True


def test_snapshot_rejects_non_file_backend() -> None:
    stele = Stele(_MemoryStore(), now=TS)
    with pytest.raises(SchemaError, match="file-store only"):
        stele.snapshot("/tmp/should-not-write", actor="ops", ts=TS)
