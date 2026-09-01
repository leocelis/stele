"""v3.6: SCM sleep/WM + GAM buffer + ACM anticipate/verify."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, scm_gam_acm_shaped_report

TS = "2026-08-21T00:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v36",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def test_scm_gam_acm(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v36", now=TS)
    lesson = stele.add(
        {
            "layer": "failure_lesson",
            "title": "Retry on 429",
            "body": "Backoff retry payment webhook on HTTP 429.",
            "scope": "project:v36",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "oracle",
                "task": "t",
                "environment": "local",
                "subject_id": "s",
                "source": "oracle:gate",
                "written_at": TS,
            },
            "usage": {"helpful": 2, "harmful": 0, "pinned": True},
        },
        ts=TS,
    )["id"]
    stele.promote(lesson, EV, actor="ci", ts=TS)

    draft = stele.add(
        {
            "layer": "issue",
            "title": "Draft",
            "body": "Buffer note about webhook retries.",
            "scope": "project:v36",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "writer",
                "task": "d",
                "environment": "local",
                "subject_id": "s",
                "source": "agent:w",
                "written_at": TS,
            },
        },
        ts=TS,
    )["id"]

    assert "importance" in stele.value_tag(
        lesson, now=TS, task_query="webhook retry"
    )
    assert lesson in stele.wm_push(lesson)["ids"]
    assert stele.sleep_trigger(force=True)["should_sleep"] is True
    plan = stele.sleep_plan(now=TS)
    assert "nrem" in plan and "rem" in plan
    assert stele.sleep_apply_nrem(actor="ops", now=TS)["count"] >= 1

    assert any(r["id"] == draft for r in stele.episodic_buffer()["buffer"])
    assert stele.semantic_boundary("webhook retry", "tomato garden soil")[
        "shift"
    ]
    assert stele.consolidate_plan()["count"] >= 1

    ant = stele.anticipate("webhook retry", consumer_scope="project:v36")
    assert "prefetch" in ant

    ok = stele.verify_compaction(
        "webhook 429",
        "Backoff retry payment webhook on HTTP 429.",
        consumer_scope="project:v36",
    )
    assert ok["ok"] is True


def test_harness_v36(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "h", store_id="h", now=TS)
    report = scm_gam_acm_shaped_report(
        stele, consumer_scope="project:demo", now=TS
    )
    assert report["suite"] == "scm_gam_acm_shaped"
    assert report["ok"] is True
