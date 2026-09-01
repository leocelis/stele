"""v3.1: StateFuse projection + TOKI operators + MemArchitect context bid."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, statefuse_toki_shaped_report

TS = "2026-08-21T00:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v31",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def test_statefuse_toki_bid(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="fuse", now=TS)
    a = stele.add(
        {
            "layer": "failure_lesson",
            "title": "Region EU",
            "body": "Primary deploy region is eu-west-1.",
            "scope": "project:v31",
            "conflict_key": "deploy:region",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "a",
                "task": "t",
                "environment": "local",
                "subject_id": "s",
                "source": "ci:a",
                "written_at": TS,
            },
        },
        ts=TS,
    )["id"]
    stele.promote(a, EV, actor="ci", ts=TS)
    b = stele.add(
        {
            "layer": "failure_lesson",
            "title": "Region US",
            "body": "Primary deploy region is us-east-1.",
            "scope": "project:v31",
            "conflict_key": "deploy:region",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "a",
                "task": "t2",
                "environment": "local",
                "subject_id": "s",
                "source": "oracle:gate",
                "written_at": TS,
            },
        },
        ts=TS,
    )["id"]
    stele.promote(b, EV, actor="ci", ts=TS)

    res = stele.project_resolve("deploy:region")
    assert res["decision"] in {"select", "abstain"}

    stele.pin_projection("deploy:region", a, actor="ci", ts=TS)
    pinned = stele.project_resolve("deploy:region")
    assert pinned["decision"] == "select"
    assert pinned["winner_id"] == a

    handle = stele.correction_handle(claim_id=a)
    assert handle["ok"] is True
    ref = stele.correction_handle(claim_ref="deploy:region")
    assert ref["ok"] is True

    plan = stele.toki_classify_operator(
        {
            "title": "Region APAC",
            "body": "Primary deploy region is ap-southeast-1.",
            "conflict_key": "deploy:region",
            "provenance": {"agent": "ci", "source": "ci:c"},
            "evidence": EV,
        },
        tip_id=a,
        evidence=EV,
    )
    assert plan["operator"] in {
        "evidence_weighted",
        "await_confirmation",
        "last_writer_wins",
        "per_rule_policy",
    }

    anomalies = stele.toki_anomaly_scan()
    assert any(f["anomaly"] == "belief_drift" for f in anomalies["findings"])

    bid = stele.context_bid("deploy region", slots=1, now=TS)
    assert bid["admitted_count"] == 1

    stele.clear_projection_pin("deploy:region")
    assert stele.list_projection_pins()["count"] == 0


def test_harness_statefuse_toki(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "h", store_id="h", now=TS)
    report = statefuse_toki_shaped_report(
        stele, consumer_scope="project:demo", now=TS
    )
    assert report["suite"] == "statefuse_toki_shaped"
    assert report["ok"] is True
