"""v3.0: STALE probes + VTA transition verify + GEM checklist."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, stale_gem_shaped_report

TS = "2026-08-21T00:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v30",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def test_stale_vta_gem(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="stale", now=TS)
    old = stele.add(
        {
            "layer": "failure_lesson",
            "title": "Office HQ",
            "body": "Primary office is in Boston near the harbor.",
            "scope": "project:v30",
            "conflict_key": "org:hq",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "a",
                "task": "t",
                "environment": "local",
                "subject_id": "s",
                "source": "ci:v1",
                "written_at": TS,
            },
        },
        ts=TS,
    )["id"]
    stele.promote(old, EV, actor="ci", ts=TS)
    sibling = stele.add(
        {
            "layer": "failure_lesson",
            "title": "Office snacks",
            "body": "Stock Boston bakery snacks in the HQ pantry.",
            "scope": "project:v30",
            "conflict_key": "org:snacks",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "a",
                "task": "t2",
                "environment": "local",
                "subject_id": "s",
                "source": "ci:s",
                "written_at": TS,
            },
        },
        ts=TS,
    )["id"]
    stele.promote(sibling, EV, actor="ci", ts=TS)
    new = stele.supersede(
        old,
        {
            "layer": "failure_lesson",
            "title": "Office HQ",
            "body": "Primary office is in Denver near the mountains.",
            "scope": "project:v30",
            "conflict_key": "org:hq",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "a",
                "task": "t3",
                "environment": "local",
                "subject_id": "s",
                "source": "ci:v2",
                "written_at": TS,
            },
        },
        actor="ci",
        ts=TS,
    )
    stele.promote(new["new_id"], EV, actor="ci", ts=TS)
    assert stele.verify_transition(old, new["new_id"])["ok"] is True
    assert stele.state_resolution(conflict_key="org:hq")["ok"] is True
    assert stele.premise_resistance(
        "Boston harbor office", consumer_scope="project:v30"
    )["refuse_premise"] is True
    assert stele.related_slot_scan("org:hq")["reverify_count"] >= 1
    assert stele.gem_report()["ok"] is True


def test_stale_gem_shaped_report(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="harness", now=TS)
    report = stale_gem_shaped_report(
        stele, consumer_scope="project:demo", now=TS
    )
    assert report["suite"] == "stale_gem_shaped"
    assert report["ok"] is True
