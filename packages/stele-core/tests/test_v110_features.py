"""v1.1: provenance purge, add_batch, diff_stores, trusted_sources, membench proxy."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, membench_shaped_report

TS = "2026-08-20T16:00:00Z"


def _entry(title: str, *, source: str = "session:ok", agent: str = "good-agent") -> dict:
    return {
        "layer": "failure_lesson",
        "title": title,
        "body": "Day-scoped keys prevent stale cross-day reads after midnight.",
        "scope": "project:v11",
        "temporal": {"valid_from": TS, "last_verified": TS},
        "provenance": {
            "agent": agent,
            "task": "cache",
            "environment": "local",
            "subject_id": "subj-v11",
            "source": source,
            "written_at": TS,
        },
    }


def test_add_batch_atomic(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="b", now=TS)
    out = stele.add_batch(
        [_entry("Batch tip one"), _entry("Batch tip two about day buckets")],
        ts=TS,
    )
    assert out["count"] == 2
    assert len(out["ids"]) == 2


def test_purge_by_provenance_dry_and_execute(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="p", now=TS)
    good = stele.add(_entry("Good day bucket tip", source="session:trusted"), ts=TS)
    bad = stele.add(_entry("Poison tip", source="web_page:evil"), ts=TS)
    for eid, issuer in ((good["id"], "ci"), (bad["id"], "ci")):
        stele.promote(
            eid,
            [
                {
                    "type": "test_result",
                    "issuer": issuer,
                    "ref": "t",
                    "observed_at": TS,
                    "verdict": "supports",
                    "command": "pytest -q",
                    "exit_status": 0,
                }
            ],
            actor="ci",
            ts=TS,
        )
    dry = stele.purge_by_provenance(
        untrusted_sources=["web_page"],
        actor="ops",
        ts=TS,
        dry_run=True,
    )
    assert dry["dry_run"] is True
    assert dry["count"] == 1
    assert dry["would_purge"][0]["id"] == bad["id"]
    assert stele.store.read_entry(bad["id"]) is not None

    done = stele.purge_by_provenance(
        untrusted_sources=["web_page"],
        actor="ops",
        ts=TS,
        dry_run=False,
    )
    assert done["count"] == 1
    assert stele.store.read_entry(bad["id"]) is None
    assert stele.store.read_entry(good["id"]) is not None


def test_diff_stores_and_trusted_sources(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "live", store_id="d", now=TS)
    a = stele.add(_entry("Day bucket alpha", source="session:a"), ts=TS)
    stele.promote(
        a["id"],
        [
            {
                "type": "human_signoff",
                "issuer": "ops",
                "ref": "ok",
                "observed_at": TS,
                "verdict": "supports",
            }
        ],
        actor="ops",
        ts=TS,
    )
    snap = tmp_path / "snap"
    stele.snapshot(snap, actor="ops", ts=TS)
    stele.add(_entry("Only live tip", source="session:b"), ts=TS)
    diff = stele.diff_stores(snap)
    assert a["id"] in diff["both"]
    assert len(diff["only_here"]) >= 1

    hits_all = stele.search("day bucket", consumer_scope="project:v11")
    hits_trust = stele.search(
        "day bucket",
        consumer_scope="project:v11",
        trusted_sources=["session:a"],
    )
    assert any(h["id"] == a["id"] for h in hits_all)
    assert all(
        (h.get("provenance") or {}).get("source") == "session:a" for h in hits_trust
    )


def test_membench_shaped_report(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="m", now=TS)
    added = stele.add(_entry("Day bucket membench"), ts=TS)
    stele.promote(
        added["id"],
        [
            {
                "type": "test_result",
                "issuer": "ci",
                "ref": "t",
                "observed_at": TS,
                "verdict": "supports",
                "command": "pytest -q",
                "exit_status": 0,
            }
        ],
        actor="ci",
        ts=TS,
    )
    report = membench_shaped_report(
        stele, query="cache buckets day", consumer_scope="project:v11", rounds=5
    )
    assert report["suite"] == "membench_shaped"
    assert report["capacity"]["total_entries"] >= 1
    assert "search_median_ms" in report["temporal_efficiency"]
