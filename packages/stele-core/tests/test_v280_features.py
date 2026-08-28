"""v2.8: MemTX transactional belief commit + action-safety + AOEP."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, memtx_aoep_shaped_report

TS = "2026-08-21T00:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v28",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def test_memtx_action_safe(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="memtx", now=TS)
    tx = stele.begin_transaction(actor="ci", ts=TS, risk_tier="irreversible")
    staged = stele.stage_write(
        tx["txid"],
        {
            "layer": "failure_lesson",
            "title": "Booking tip",
            "body": "Confirm inventory before placing an irreversible booking tool call.",
            "scope": "project:v28",
            "conflict_key": "policy:book",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "oracle",
                "task": "t",
                "environment": "local",
                "subject_id": "s",
                "source": "ci:gate",
                "written_at": TS,
            },
        },
        actor="ci",
        ts=TS,
    )
    eid = staged["id"]
    assert stele.action_safe_gate([eid])["allowed"] is False
    assert stele.validate_transaction(tx["txid"])["ok"] is True
    assert stele.commit_transaction(tx["txid"], EV, actor="ci", ts=TS)["ok"]
    assert stele.action_safe_gate([eid])["allowed"] is True

    tx2 = stele.begin_transaction(actor="ci", ts=TS)
    stele.stage_write(
        tx2["txid"],
        {
            "layer": "failure_lesson",
            "title": "Booking tip draft",
            "body": "Confirm inventory twice before placing an irreversible booking tool call.",
            "scope": "project:v28",
            "conflict_key": "policy:book",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "a",
                "task": "t2",
                "environment": "local",
                "subject_id": "s",
                "source": "session:draft",
                "written_at": TS,
            },
        },
        actor="ci",
        ts=TS,
    )
    assert stele.action_safe_gate([eid])["allowed"] is False
    stele.abort_transaction(tx2["txid"], actor="ci", ts=TS)
    assert stele.in_flight_report()["count_open"] == 0
    assert stele.aoep_report()["ok"] is True


def test_memtx_aoep_shaped_report(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="harness", now=TS)
    report = memtx_aoep_shaped_report(
        stele, consumer_scope="project:demo", now=TS
    )
    assert report["suite"] == "memtx_aoep_shaped"
    assert report["ok"] is True
