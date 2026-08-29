"""MySQL SteleStore parity — runs only when STELE_STORE_DSN + CA are set.

Never prints DSN. Skip cleanly in CI without secrets.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("STELE_STORE_DSN")
    or not (os.environ.get("STELE_MYSQL_SSL_CA") or os.environ.get("STELE_MYSQL_SSL_CA_B64")),
    reason="STELE_STORE_DSN + TLS CA not configured",
)

TS = "2026-08-29T12:00:00Z"
EVIDENCE = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "tests/test_mysql_store.py",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def test_mysql_add_promote_search_roundtrip(tmp_path: Path) -> None:
    from stele_core import Stele

    scratch = tmp_path / "scratch"
    stele = Stele.open(
        scratch,
        store_id=os.environ.get("STELE_STORE_ID", "stele_test"),
        now=TS,
        dsn=os.environ["STELE_STORE_DSN"],
    )
    entry = {
        "layer": "failure_lesson",
        "title": "hosted mysql roundtrip",
        "body": "agents must not self-promote; calendar buckets cache lesson",
        "scope": "project:stele-mysql-test",
        "temporal": {"valid_from": TS, "last_verified": TS},
        "provenance": {
            "agent": "proof-agent",
            "task": "mysql-parity",
            "environment": "local",
            "subject_id": "subj-mysql",
            "source": "session:mysql-test",
            "written_at": TS,
            "model_id": "model-a",
        },
    }
    added = stele.add(entry, ts=TS)
    eid = added["id"]
    assert added["state"] == "quarantined"
    assert stele.store.read_entry(eid) is not None
    assert stele.search("calendar buckets", consumer_scope="project:stele-mysql-test") == []

    with pytest.raises(Exception) as excinfo:
        stele.promote(eid, EVIDENCE, actor="proof-agent", ts=TS)
    assert "writer cannot promote" in str(excinfo.value).lower() or "writer" in str(
        excinfo.value
    ).lower()

    stele.promote(eid, EVIDENCE, actor="ci", ts=TS)
    hits = stele.search("calendar buckets", consumer_scope="project:stele-mysql-test")
    assert any(h.get("id") == eid for h in hits)

    dig = stele.store.put_attachment(b"stele-mysql-blob")
    assert stele.store.verify_attachment_digest(dig)

    # Hosted regression: doctor must not require file-layout attrs
    assert not hasattr(stele.store, "manifest_path")
    doc = stele.doctor(now=TS)
    assert doc["ok"] is True
    assert doc["verify"]["ok"] is True
    assert doc["stats"]["total"] >= 1

    stele.store.delete_entry_file(eid, actor="ci", ts="2026-08-29T12:02:00Z", reason="test cleanup")
    assert stele.store.read_entry(eid) is None
