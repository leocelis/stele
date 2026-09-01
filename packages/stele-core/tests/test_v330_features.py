"""v3.3: TierMem escalate/write-back + MSCE skill crystallization."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, tiermem_msce_shaped_report

TS = "2026-08-21T00:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v33",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def test_tiermem_msce(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v33", now=TS)
    raw = stele.put_raw_page(
        "Payment webhook id=99 failed checksum=deadbeef at 12:01Z",
        actor="ci",
        ts=TS,
    )
    assert raw["digest"]

    wb = stele.verified_writeback(
        title="Webhook failure",
        body="Payment webhook failed; see raw for checksum.",
        scope="project:v33",
        raw_digests=[raw["digest"]],
        actor="ci",
        ts=TS,
        promote=True,
        evidence=EV,
    )
    assert wb["state"] == "promoted"

    gate = stele.sufficiency_gate(
        "exact checksum deadbeef webhook id 99",
        consumer_scope="project:v33",
    )
    assert gate["decision"] == "miss"

    esc = stele.escalate_raw([wb["id"]])
    assert esc["ok"] is True
    assert "deadbeef" in esc["pages"][0]["text"]

    lesson = stele.add(
        {
            "layer": "failure_lesson",
            "title": "Verify checksum first",
            "body": "Reject webhooks with bad checksum before debit.",
            "scope": "project:v33",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "a",
                "task": "t",
                "environment": "local",
                "subject_id": "s",
                "source": "ci:a",
                "written_at": TS,
            },
            "usage": {"helpful": 2, "harmful": 0, "pinned": True},
            "links": [{"kind": "entry", "ref": wb["id"]}],
        },
        ts=TS,
    )["id"]
    stele.promote(lesson, EV, actor="ci", ts=TS)
    assert stele.skill_eligibility(lesson)["eligible"] is True

    crystal = stele.crystallize_skill([lesson], write=True, actor="ci", ts=TS)
    assert crystal["ok"] is True
    assert crystal["id"]

    assert stele.skill_catalog()["count"] >= 1

    bf = stele.value_backfill(
        lesson, terminal_success=True, apply=True, actor="ci", ts=TS
    )
    assert bf["applied"] is True
    assert bf["usage_after"]["helpful"] >= 3


def test_harness_v33(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "h", store_id="h", now=TS)
    report = tiermem_msce_shaped_report(
        stele, consumer_scope="project:demo", now=TS
    )
    assert report["suite"] == "tiermem_msce_shaped"
    assert report["ok"] is True
