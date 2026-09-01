"""Additional intent-gap coverage: writer ban, domain scope, stale, as_of, reflect, hybrid."""

from __future__ import annotations

from pathlib import Path

import pytest

from helpers import TS, base_entry, oracle_evidence
from stele_core import SchemaError, Stele


def test_writer_cannot_promote_own_claim(stele: Stele) -> None:
    eid = stele.add(base_entry(), ts=TS)["id"]
    with pytest.raises(SchemaError, match="writer cannot promote"):
        stele.promote(eid, oracle_evidence(issuer="ci"), actor="agent-a", ts=TS)


def test_domain_scope_visible_with_consumer_domain(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="d", now=TS)
    eid = stele.add(
        base_entry(
            title="Domain cache guidance",
            body="Domain-wide day bucket rule.",
            scope="domain:caching",
        ),
        ts=TS,
    )["id"]
    stele.promote(eid, oracle_evidence(), actor="ci", ts=TS)

    assert stele.search("bucket", consumer_scope="project:demo") == []
    hits = stele.search(
        "bucket", consumer_scope="project:demo", consumer_domain="domain:caching"
    )
    assert [h["id"] for h in hits] == [eid]


def test_staleness_flag(tmp_path: Path) -> None:
    stele = Stele.open(
        tmp_path / "s",
        store_id="stale",
        now=TS,
        staleness_horizon="2026-08-19T00:00:00Z",
    )
    eid = stele.add(
        base_entry(
            temporal={
                "valid_from": "2026-01-01T00:00:00Z",
                "last_verified": "2026-01-01T00:00:00Z",
            },
            provenance={
                "agent": "agent-a",
                "task": "t",
                "environment": "e",
                "subject_id": "s",
                "source": "session:1",
                "written_at": "2026-01-01T00:00:00Z",
            },
        ),
        ts=TS,
    )["id"]
    stele.promote(eid, oracle_evidence(), actor="ci", ts="2026-01-01T00:00:00Z")
    hits = stele.search("cache", consumer_scope="project:demo")
    assert len(hits) == 1
    assert hits[0]["stale"] is True


def test_as_of_historical_superseded(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="hist", now=TS)
    old = stele.add(base_entry(title="Old cache lesson", body="Old day bucket advice."), ts=TS)
    stele.promote(old["id"], oracle_evidence(), actor="ci", ts=TS)
    stele.supersede(
        old["id"],
        base_entry(title="New cache lesson", body="New day bucket advice v2."),
        actor="maint",
        ts=TS,
    )
    # Default search hides superseded
    assert stele.search("cache", consumer_scope="project:demo") == []
    # Point-in-time before supersession — re-seed with earlier valid_from
    stele2 = Stele.open(tmp_path / "s2", store_id="hist2", now=TS)
    old2 = stele2.add(
        base_entry(
            title="Historical cache lesson",
            body="Advice valid in July.",
            temporal={
                "valid_from": "2026-07-01T00:00:00Z",
                "last_verified": "2026-07-01T00:00:00Z",
            },
            provenance={
                "agent": "agent-a",
                "task": "t",
                "environment": "e",
                "subject_id": "s",
                "source": "session:1",
                "written_at": "2026-07-01T00:00:00Z",
            },
        ),
        ts="2026-07-01T00:00:00Z",
    )
    stele2.promote(old2["id"], oracle_evidence(), actor="ci", ts="2026-07-01T00:00:00Z")
    stele2.supersede(
        old2["id"],
        base_entry(
            title="Replacement",
            body="New advice.",
            temporal={"valid_from": TS, "last_verified": TS},
        ),
        actor="maint",
        ts=TS,
    )
    hits = stele2.search(
        "Historical cache",
        consumer_scope="project:demo",
        as_of="2026-07-15T00:00:00Z",
    )
    assert len(hits) == 1
    assert hits[0]["id"] == old2["id"]
    assert hits[0]["historical"] is True


def test_reflect_preserves_provenance(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="ref", now=TS)
    a = stele.add(base_entry(title="Same cache tip alpha", body="Day buckets matter."), ts=TS)
    b = stele.add(
        base_entry(
            title="Same cache tip beta",
            body="Day buckets matter a lot.",
            provenance={
                "agent": "agent-b",
                "task": "t2",
                "environment": "e",
                "subject_id": "s2",
                "source": "session:2",
                "written_at": TS,
            },
        ),
        ts=TS,
    )
    stele.promote(a["id"], oracle_evidence(issuer="ci1"), actor="ci1", ts=TS)
    stele.promote(b["id"], oracle_evidence(issuer="ci2"), actor="ci2", ts=TS)
    report = stele.reflect(actor="maint", ts=TS, similarity_threshold=0.5)
    assert report["merged"]
    kept_id = report["merged"][0]["kept"]
    kept = stele.store.read_entry(kept_id)
    assert kept is not None
    refs = [lnk.get("ref", "") for lnk in kept.get("links") or []]
    assert any("merged-from:" in r for r in refs)
    assert any(report["merged"][0]["dropped"] in r for r in refs)


def test_hybrid_semantic_on_search_not_write(tmp_path: Path) -> None:
    class Emb:
        def __init__(self) -> None:
            self.calls = 0

        def embed(self, texts):  # type: ignore[no-untyped-def]
            self.calls += 1
            return [[float(len(t)), 1.0] for t in texts]

    emb = Emb()
    stele = Stele.open(tmp_path / "s", store_id="hyb", now=TS, embedder=emb)
    eid = stele.add(base_entry(), ts=TS)["id"]
    stele.promote(eid, oracle_evidence(), actor="ci", ts=TS)
    assert emb.calls == 0
    hits = stele.search("cache", consumer_scope="project:demo")
    assert len(hits) == 1
    assert emb.calls >= 1
