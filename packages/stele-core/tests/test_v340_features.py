"""v3.4: FadeMem dual-layer fade + SSGM Weibull + MemR3 reflective gap."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, fademem_memr3_shaped_report

TS = "2026-08-21T00:00:00Z"
OLD = "2025-01-01T00:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v34",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def test_fademem_memr3(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v34", now=TS)
    stale = stele.add(
        {
            "layer": "failure_lesson",
            "title": "Old tip",
            "body": "Clear redis cache before deploy.",
            "scope": "project:v34",
            "conflict_key": "ops:cache",
            "temporal": {"valid_from": OLD, "last_verified": OLD},
            "provenance": {
                "agent": "oracle",
                "task": "old",
                "environment": "local",
                "subject_id": "subj-v34",
                "source": "ci:old",
                "written_at": OLD,
            },
            "usage": {"helpful": 0, "harmful": 0},
        },
        ts=TS,
    )["id"]
    # Promote on an old clock so last_verified stays aged (promote stamps ts).
    stele.promote(stale, EV, actor="ci", ts=OLD)

    fresh = stele.add(
        {
            "layer": "failure_lesson",
            "title": "New tip",
            "body": "Flush redis cache key namespace payments before deploy.",
            "scope": "project:v34",
            "conflict_key": "ops:cache",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "oracle",
                "task": "new",
                "environment": "local",
                "subject_id": "subj-v34",
                "source": "oracle:gate",
                "written_at": TS,
            },
            "usage": {"helpful": 2, "harmful": 0, "pinned": True},
        },
        ts=TS,
    )["id"]
    stele.promote(fresh, EV, actor="ci", ts=TS)

    strength = stele.fade_strength(stale, now=TS)
    assert strength["fade_layer"] in {"sml", "lml"}
    assert float(strength["strength"]) < 0.5

    scan = stele.fade_scan(now=TS, threshold=0.5)
    assert any(f["id"] == stale for f in scan["faded"])

    fuse = stele.fusion_candidates(min_overlap=0.2)
    assert fuse["count"] >= 1

    wb = stele.weibull_relevance(fresh, now=TS)
    assert float(wb["weibull_relevance"]) > 0.5

    hits = stele.search(
        "cache", consumer_scope="project:v34", min_weibull=0.01
    )
    assert isinstance(hits, list)
    assert all("weibull_relevance" in h for h in hits)

    plan = stele.reflective_retrieve(
        "redis payments namespace flush code 42",
        consumer_scope="project:v34",
    )
    assert "next_probes" in plan
    assert "gap" in plan

    gap = plan["gap"]
    upd = stele.gap_tracker_update(
        gap.get("gaps") or [],
        query="payments namespace 42",
        consumer_scope="project:v34",
    )
    assert "remaining_count" in upd

    eg = stele.evidence_gap("cache", consumer_scope="project:v34")
    assert "coverage" in eg


def test_harness_v34(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "h", store_id="h", now=TS)
    report = fademem_memr3_shaped_report(
        stele, consumer_scope="project:demo", now=TS
    )
    assert report["suite"] == "fademem_memr3_shaped"
    assert report["ok"] is True
