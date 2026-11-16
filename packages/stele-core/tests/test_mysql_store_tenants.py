"""MySQL store ids and per-store roots (TECH_SPEC §12.2 ST2a) + listing (§12.4 ST4).

Runs against the in-process fake in ``fake_mysql.py`` — never a hosted database.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fake_mysql import FAKE_DSN, FakeMySQLServer
from stele_core import Stele
from stele_core.schema import SchemaError
from stele_core.store import StoreError

TS = "2026-11-16T12:00:00Z"


def _entry(title: str, body: str, scope: str = "project:tenant-test") -> dict:
    return {
        "layer": "failure_lesson",
        "title": title,
        "body": body,
        "scope": scope,
        "temporal": {"valid_from": TS, "last_verified": TS},
        "provenance": {
            "agent": "writer-agent",
            "task": "tenant-test",
            "environment": "local",
            "subject_id": "subj-1",
            "source": "session:tenant-test",
            "written_at": TS,
        },
    }


@pytest.fixture
def fake_db(monkeypatch) -> FakeMySQLServer:
    server = FakeMySQLServer()
    server.install(monkeypatch)
    return server


def test_given_id_creates_its_own_row_and_never_adopts(fake_db, tmp_path: Path) -> None:
    fake_db.add_store_row("store_operator01")
    operator_entry_key = ("store_operator01", "e-op")
    fake_db.entries[operator_entry_key] = {"state": "promoted", "body_json": "{}"}

    s = Stele.open(tmp_path / "t-acme", store_id="t-acme", now=TS, dsn=FAKE_DSN)
    assert s.store.store_id == "t-acme"
    assert set(fake_db.meta) == {"store_operator01", "t-acme"}

    added = s.add(_entry("tenant lesson", "only acme writes this"), ts=TS)
    assert (("t-acme", added["id"])) in fake_db.entries
    assert all(k[0] != "store_operator01" or k == operator_entry_key for k in fake_db.entries)
    assert [e["id"] for e in s.store.iter_entries()] == [added["id"]]


def test_given_id_on_create_false_refuses_instead_of_adopting(fake_db, tmp_path: Path) -> None:
    fake_db.add_store_row("store_operator01")
    with pytest.raises(StoreError, match="t-ghost"):
        Stele.open(tmp_path / "g", store_id="t-ghost", now=TS, dsn=FAKE_DSN, create=False)


def test_no_id_adopts_operator_store_never_a_tenant_store(fake_db, tmp_path: Path) -> None:
    fake_db.add_store_row("t-aaa")
    fake_db.add_store_row("store_operator01")
    s = Stele.open(tmp_path / "op", now=TS, dsn=FAKE_DSN)
    assert s.store.store_id == "store_operator01"
    s2 = Stele.open(tmp_path / "op2", now=TS, dsn=FAKE_DSN, create=False)
    assert s2.store.store_id == "store_operator01"


def test_no_id_with_only_tenant_rows_creates_a_fresh_store(fake_db, tmp_path: Path) -> None:
    fake_db.add_store_row("t-aaa")
    s = Stele.open(tmp_path / "op", now=TS, dsn=FAKE_DSN)
    assert s.store.store_id != "t-aaa"
    assert s.store.store_id in fake_db.meta


def test_existing_id_reopens_same_row(fake_db, tmp_path: Path) -> None:
    fake_db.add_store_row("store_operator01")
    s = Stele.open(tmp_path / "op", store_id="store_operator01", now=TS, dsn=FAKE_DSN)
    assert s.store.store_id == "store_operator01"
    assert set(fake_db.meta) == {"store_operator01"}


def test_drop_indexes_touches_only_its_own_root(fake_db, tmp_path: Path) -> None:
    a = Stele.open(tmp_path / "t-a", store_id="t-a", now=TS, dsn=FAKE_DSN)
    b = Stele.open(tmp_path / "t-b", store_id="t-b", now=TS, dsn=FAKE_DSN)
    marker = b.store.index_dir / "lexical" / "keep.bin"
    marker.write_bytes(b"x")
    a.store.drop_indexes()
    assert marker.exists()


def test_list_entries_pages_and_filters(fake_db, tmp_path: Path) -> None:
    s = Stele.open(tmp_path / "t-acme", store_id="t-acme", now=TS, dsn=FAKE_DSN)
    ids = [s.add(_entry(f"lesson {i}", f"body number {i}"), ts=TS)["id"] for i in range(5)]
    evidence = [
        {
            "type": "test_result",
            "issuer": "ci",
            "ref": "tests/x.py",
            "observed_at": TS,
            "verdict": "supports",
            "command": "pytest -q",
            "exit_status": 0,
        }
    ]
    s.promote(ids[0], evidence, actor="ci", ts=TS)

    seen: list[str] = []
    cursor = None
    pages = 0
    while True:
        page = s.list_entries(limit=2, cursor=cursor)
        pages += 1
        for row in page["entries"]:
            assert set(row) == {"id", "layer", "title", "state", "written_at"}
            assert row["written_at"] == TS
            assert row["layer"] == "failure_lesson"
        seen.extend(r["id"] for r in page["entries"])
        cursor = page["next_cursor"]
        if cursor is None:
            break
    assert pages == 3
    assert seen == sorted(ids)

    promoted = s.list_entries(state="promoted")
    assert [r["id"] for r in promoted["entries"]] == [ids[0]]
    assert promoted["next_cursor"] is None
    quarantined = s.list_entries(state="quarantine")
    assert sorted(r["id"] for r in quarantined["entries"]) == sorted(ids[1:])
    assert all(r["state"] == "quarantined" for r in quarantined["entries"])

    assert len(s.list_entries(limit=10_000)["entries"]) == 5
    with pytest.raises(SchemaError):
        s.list_entries(state="archived")
