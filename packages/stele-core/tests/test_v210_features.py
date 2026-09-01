"""v2.1: decision receipts, verify_import, policy_manifest, lineage trust."""

from __future__ import annotations

from pathlib import Path

import pytest

from stele_core import Stele, SchemaError, pam_cava_shaped_report

TS = "2026-08-21T00:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v21",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def _entry(title: str, *, conflict_key: str | None = None) -> dict:
    e = {
        "layer": "failure_lesson",
        "title": title,
        "body": f"{title} body with enough tokens for decision and lineage tests.",
        "scope": "project:v21",
        "temporal": {"valid_from": TS, "last_verified": TS},
        "provenance": {
            "agent": "agent",
            "task": "t",
            "environment": "local",
            "subject_id": "subj-v21",
            "source": "session:ok",
            "written_at": TS,
        },
    }
    if conflict_key:
        e["conflict_key"] = conflict_key
    return e


def test_decision_receipt_on_release(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="dr", now=TS)
    eid = stele.add(_entry("Release tip"), ts=TS)["id"]
    stele.promote(eid, EV, actor="ci", ts=TS)
    gate = stele.release_gate(
        now=TS, issue_receipt=True, actor="ci", claim_ids=[eid]
    )
    assert gate["released"] is True
    assert gate["receipt"]["kind"] == "release"
    listed = stele.list_decision_receipts()
    assert listed[0]["id"] == gate["receipt"]["id"]
    v = stele.verify_decision_receipt(gate["receipt"], require_current_head=True)
    assert v["ok"] is True


def test_verify_import_and_policy(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="imp", now=TS)
    eid = stele.add(_entry("Pack tip"), ts=TS)["id"]
    stele.promote(eid, EV, actor="ci", ts=TS)
    pack = tmp_path / "pack"
    manifest = stele.export(
        pack,
        scope="project:v21",
        audience="practitioner",
        purpose="test",
        created_at=TS,
        expiry="2099-01-01T00:00:00Z",
    )
    assert manifest.get("policy_digest")
    assert (pack / "policy_manifest.json").is_file()
    ok = stele.verify_import(pack)
    assert ok["ok"] is True
    bad = stele.verify_import(pack, expected_policy_digest="deadbeef")
    assert bad["ok"] is False
    assert bad["halted_at"] == "policy_digest"
    dest = Stele.open(tmp_path / "dest", store_id="dest", now=TS)
    with pytest.raises(SchemaError):
        dest.hydrate(
            pack,
            actor="ci",
            ts=TS,
            require_verify=True,
            expected_policy_digest="deadbeef",
        )


def test_lineage_trust_refuse(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="lin", now=TS)
    clean = stele.add(_entry("Clean tip"), ts=TS)["id"]
    poison = stele.add(_entry("Poison tip", conflict_key="v21:p"), ts=TS)["id"]
    stele.promote(clean, EV, actor="ci", ts=TS)
    stele.promote(poison, EV, actor="ci", ts=TS)
    stele.link(clean, kind="entry", ref=poison, actor="ci", ts=TS)
    stele.revoke_by_key("v21:p", evidence=EV, actor="ci", ts=TS)
    lt = stele.lineage_trust(clean)
    assert lt["label"] == "Derived-Untrusted"
    hits = stele.search(
        "Clean", consumer_scope="project:v21", refuse_untrusted_lineage=True
    )
    assert clean not in {h["id"] for h in hits}


def test_pam_cava_shaped_report(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="harness", now=TS)
    report = pam_cava_shaped_report(stele, consumer_scope="project:demo", now=TS)
    assert report["suite"] == "pam_cava_shaped"
    assert report["ok"] is True
