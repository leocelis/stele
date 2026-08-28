"""v2.4: MemIR typed roles, fact interface, D-Mem dual channel."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, memir_dmem_shaped_report

TS = "2026-08-21T00:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v24",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def test_roles_and_dual_channel(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="memir", now=TS)
    claim = stele.add(
        {
            "layer": "failure_lesson",
            "title": "Claim tip",
            "body": "Claim tip body with enough tokens for role tests.",
            "scope": "project:v24",
            "memory_role": "claim",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "a",
                "task": "t",
                "environment": "local",
                "subject_id": "s",
                "source": "session:c",
                "written_at": TS,
            },
        },
        ts=TS,
    )["id"]
    evid = stele.add(
        {
            "layer": "issue",
            "title": "Evidence tip",
            "body": "Evidence tip body with enough tokens for role tests.",
            "scope": "project:v24",
            "memory_role": "evidence",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "a",
                "task": "t",
                "environment": "local",
                "subject_id": "s",
                "source": "session:e",
                "written_at": TS,
            },
        },
        ts=TS,
    )["id"]
    stele.promote(claim, EV, actor="ci", ts=TS)
    stele.promote(evid, EV, actor="ci", ts=TS)
    iface = stele.fact_interface([claim, evid])
    assert claim in iface["authorize_ids"]
    assert evid not in iface["authorize_ids"]
    assert stele.claim_closure([claim], require_claim_role=True)["closed"] is True
    assert stele.claim_closure([evid], require_claim_role=True)["closed"] is False
    hits = stele.search("tip", consumer_scope="project:v24", claims_only=True)
    assert evid not in {h["id"] for h in hits}
    dual = stele.dual_channel_search("tip", consumer_scope="project:v24")
    assert "quality_gate" in dual


def test_memir_dmem_shaped_report(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="harness", now=TS)
    report = memir_dmem_shaped_report(stele, consumer_scope="project:demo", now=TS)
    assert report["suite"] == "memir_dmem_shaped"
    assert report["ok"] is True
