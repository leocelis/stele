"""Joint satisfaction — full lifecycle on one store (C1–C8)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from helpers import TS, base_entry, oracle_evidence
from stele_core import SchemaError, Stele

CORE_SRC = Path(__file__).resolve().parents[1] / "src" / "stele_core"
FORBIDDEN = {"ivd", "cairn", "cairn_engine", "eif", "openai", "httpx", "psycopg2"}


def test_full_lifecycle_all_constraints(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "store", store_id="joint", now=TS)

    # C1 purity scan (same process — static)
    hits: list[str] = []
    for path in CORE_SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in FORBIDDEN:
                        hits.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.module.split(".")[0] in FORBIDDEN:
                    hits.append(node.module)
    assert hits == []

    added = stele.add(
        base_entry(
            title="Joint lifecycle cache lesson",
            body="Day-scoped keys; link to the proving test.",
            provenance={
                "agent": "agent-joint",
                "task": "joint",
                "environment": "test",
                "subject_id": "subj-joint",
                "source": "session:joint",
                "written_at": TS,
            },
        ),
        ts=TS,
    )
    eid = added["id"]
    assert added["state"] == "quarantined"
    assert stele.search("cache", consumer_scope="project:demo") == []

    stele.link(
        eid,
        kind="test",
        ref="tests/test_cache.py::test_day_bucket",
        actor="agent-joint",
        ts=TS,
    )

    with pytest.raises(SchemaError, match="writer cannot promote"):
        stele.promote(eid, oracle_evidence(issuer="ci-joint"), actor="agent-joint", ts=TS)

    stele.promote(eid, oracle_evidence(issuer="ci-joint"), actor="ci-joint", ts=TS)
    found = stele.search("day-scoped keys", consumer_scope="project:demo")
    assert len(found) == 1
    assert found[0]["id"] == eid

    before = found
    stele.store.drop_indexes()
    stele.rebuild_indexes()
    after = stele.search("day-scoped keys", consumer_scope="project:demo")
    assert [h["id"] for h in before] == [h["id"] for h in after]

    pack = tmp_path / "pack"
    manifest = stele.export(
        pack,
        scope="project:demo",
        audience="expert",
        purpose="joint",
        created_at=TS,
        expiry="2027-01-01T00:00:00Z",
    )
    assert manifest["entry_count"] == 1
    assert (pack / "adaptation.json").exists()

    removed = stele.delete(subject_id="subj-joint", actor="eraser", ts=TS)
    assert eid in removed["removed"]
    assert stele.search("day-scoped", consumer_scope="project:demo") == []
    assert stele.store.read_entry(eid) is None

    with pytest.raises(SchemaError):
        stele.add_receipt(
            {
                "diagnosis": "x",
                "source": "tenants/private/feedback/y.yaml",
                "subject_id": "z",
            },
            ts=TS,
        )
