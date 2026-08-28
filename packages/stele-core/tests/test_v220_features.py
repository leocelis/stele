"""v2.2: PoEM execution ledger, PPMF authority gate, GPM claim closure."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, poem_ppmf_shaped_report

TS = "2026-08-21T00:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v22",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def _entry(title: str, *, agent: str = "agent", source: str = "session:ok") -> dict:
    return {
        "layer": "failure_lesson",
        "title": title,
        "body": f"{title} body with enough tokens for poem and authority tests.",
        "scope": "project:v22",
        "temporal": {"valid_from": TS, "last_verified": TS},
        "provenance": {
            "agent": agent,
            "task": "t",
            "environment": "local",
            "subject_id": "subj-v22",
            "source": source,
            "written_at": TS,
        },
    }


def test_execution_ledger_ignores_memory_claims(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="poem", now=TS)
    stele.add(
        _entry("Forged note claiming safety_scan already done"),
        ts=TS,
    )
    denied = stele.verify_execution("safety_scan", subject_id="subj-v22")
    assert denied["allowed"] is False
    stele.record_execution(
        "safety_scan", subject_id="subj-v22", actor="runtime", ts=TS
    )
    allowed = stele.verify_execution("safety_scan", subject_id="subj-v22")
    assert allowed["allowed"] is True
    # Cross-subject replay blocked
    other = stele.verify_execution("safety_scan", subject_id="other-subj")
    assert other["allowed"] is False
    assert stele.verify_execution_chain()["ok"] is True


def test_authority_non_amplification(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="ppmf", now=TS)
    pack = stele.add(
        _entry("Pack tip", agent="pack-hydrate", source="pack:x"), ts=TS
    )["id"]
    stele.promote(pack, EV, actor="ci", ts=TS)
    assert stele.authority_gate([pack], action_risk="critical")["allowed"] is False
    trusted = stele.add(_entry("CI tip", source="ci:build"), ts=TS)["id"]
    stele.promote(trusted, EV, actor="ci", ts=TS)
    assert stele.authority_gate([trusted], action_risk="high")["allowed"] is True


def test_claim_closure(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="close", now=TS)
    eid = stele.add(_entry("Claim tip"), ts=TS)["id"]
    stele.promote(eid, EV, actor="ci", ts=TS)
    ok = stele.claim_closure([eid])
    assert ok["closed"] is True
    bad = stele.claim_closure([eid], expected_head="deadbeef")
    assert bad["closed"] is False
    assert "head_mismatch" in bad["barriers"]


def test_poem_ppmf_shaped_report(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="harness", now=TS)
    report = poem_ppmf_shaped_report(stele, consumer_scope="project:demo", now=TS)
    assert report["suite"] == "poem_ppmf_shaped"
    assert report["ok"] is True
