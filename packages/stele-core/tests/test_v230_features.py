"""v2.3: MemoRepair-shaped cascade withdraw, repair plan, non-revival."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, memorepair_shaped_report

TS = "2026-08-21T00:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v23",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def _entry(title: str) -> dict:
    return {
        "layer": "failure_lesson",
        "title": title,
        "body": f"{title} body with enough tokens for cascade repair tests.",
        "scope": "project:v23",
        "temporal": {"valid_from": TS, "last_verified": TS},
        "provenance": {
            "agent": "agent",
            "task": "t",
            "environment": "local",
            "subject_id": "subj-v23",
            "source": "session:ok",
            "written_at": TS,
        },
    }


def test_cascade_withdraw_and_plan(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="mr", now=TS)
    fault = stele.add(_entry("Fault tip"), ts=TS)["id"]
    child = stele.add(_entry("Child tip"), ts=TS)["id"]
    stele.promote(fault, EV, actor="ci", ts=TS)
    stele.promote(child, EV, actor="ci", ts=TS)
    stele.link(child, kind="entry", ref=fault, actor="ci", ts=TS)
    impact = stele.cascade_impact(fault)
    assert child in impact["ids"]
    assert stele.cascade_exposure(fault)["promoted_exposed"] == 1
    plan = stele.repair_plan(fault)
    assert child in plan["selected"]
    wd = stele.withdraw_cascade(fault, evidence=EV, actor="ci", ts=TS)
    assert wd["exposure_after"]["promoted_exposed"] == 0
    probe = stele.non_revival_probe(
        consumer_scope="project:v23", forbidden_ids=[fault, child], probe_query="tip"
    )
    assert probe["ok"] is True


def test_memorepair_shaped_report(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="harness", now=TS)
    report = memorepair_shaped_report(stele, consumer_scope="project:demo", now=TS)
    assert report["suite"] == "memorepair_shaped"
    assert report["ok"] is True
