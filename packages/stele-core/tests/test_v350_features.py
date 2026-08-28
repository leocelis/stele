"""v3.5: reversible archive + SF-AMS CIS + MemCon control suggest."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, archive_sfams_memcon_shaped_report

TS = "2026-08-21T00:00:00Z"
OLD = "2025-01-01T00:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v35",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def test_archive_sfams_memcon(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v35", now=TS)
    issue = stele.add(
        {
            "layer": "issue",
            "title": "Old queue note",
            "body": "Triage note about backlog depth.",
            "scope": "project:v35",
            "temporal": {"valid_from": OLD, "last_verified": OLD},
            "provenance": {
                "agent": "oracle",
                "task": "old",
                "environment": "local",
                "subject_id": "subj-v35",
                "source": "ci:old",
                "written_at": OLD,
            },
            "usage": {"helpful": 0, "harmful": 0},
        },
        ts=TS,
    )["id"]
    stele.promote(issue, EV, actor="ci", ts=OLD)

    plan = stele.archive_plan(now=TS, min_age_days=7)
    assert any(c["id"] == issue for c in plan["candidates"])

    applied = stele.archive_apply([issue], actor="ops", ts=TS)
    assert issue in applied["archived"]

    hits = stele.search("backlog", consumer_scope="project:v35")
    assert all(h["id"] != issue for h in hits)

    assert stele.list_archived()["count"] >= 1
    assert stele.unarchive(issue, actor="ops", ts=TS)["state"] == "promoted"

    lesson = stele.add(
        {
            "layer": "failure_lesson",
            "title": "Verify invoice",
            "body": "Check invoice id before payment.",
            "scope": "project:v35",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "oracle",
                "task": "pay",
                "environment": "local",
                "subject_id": "subj-v35",
                "source": "oracle:gate",
                "written_at": TS,
            },
            "usage": {"helpful": 4, "harmful": 0, "pinned": True},
        },
        ts=TS,
    )["id"]
    stele.promote(lesson, EV, actor="ci", ts=TS)

    cis = stele.composite_importance(lesson, now=TS)
    assert cis["tier"] in {"core", "important", "secondary", "irrelevant"}
    assert stele.cis_scan(now=TS)["count"] >= 1

    ctrl = stele.control_suggest(
        "invoice payment verify", consumer_scope="project:v35"
    )
    assert ctrl["action"] in {
        "NO_OP",
        "RETRIEVE",
        "RE_RETRIEVE",
        "CONSOLIDATE",
        "FORGET",
        "PLAN_INJECT",
    }


def test_harness_v35(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "h", store_id="h", now=TS)
    report = archive_sfams_memcon_shaped_report(
        stele, consumer_scope="project:demo", now=TS
    )
    assert report["suite"] == "archive_sfams_memcon_shaped"
    assert report["ok"] is True
