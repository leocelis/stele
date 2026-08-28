"""v1.7: lifecycle tiers, TEPA revoke, pack seal, search_explain."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, tepa_amvl_shaped_report

TS = "2026-08-20T23:30:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v17",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def _entry(title: str, *, key: str | None = None, pinned: bool = False) -> dict:
    e = {
        "layer": "failure_lesson",
        "title": title,
        "body": f"{title} body with enough tokens for retrieval ranking.",
        "scope": "project:v17",
        "temporal": {"valid_from": TS, "last_verified": TS},
        "provenance": {
            "agent": "agent",
            "task": "t",
            "environment": "local",
            "subject_id": "subj-v17",
            "source": "session:ok",
            "written_at": TS,
        },
    }
    if key:
        e["conflict_key"] = key
    if pinned:
        e["usage"] = {"helpful": 2, "harmful": 0, "ignored": 0, "pinned": True}
    return e


def test_lifecycle_and_tier_filter(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="life", now=TS)
    hot = stele.add(_entry("Hot tip", pinned=True), ts=TS)["id"]
    cold = stele.add(
        {
            **_entry("Cold tip"),
            "temporal": {
                "valid_from": "2025-01-01T00:00:00Z",
                "last_verified": "2025-01-01T00:00:00Z",
            },
        },
        ts=TS,
    )["id"]
    stele.promote(hot, EV, actor="ci", ts=TS)
    stele.promote(cold, EV, actor="ci", ts=TS)
    # Promote refreshes last_verified — push cold back past warm horizon.
    stele.update(
        cold,
        {
            "temporal": {
                "valid_from": "2025-01-01T00:00:00Z",
                "last_verified": "2025-01-01T00:00:00Z",
            }
        },
        actor="ops",
        ts=TS,
    )
    inv = stele.lifecycle_inventory(now=TS)
    assert hot in inv["ids"]["hot"]
    assert cold in inv["ids"]["cold"]
    hits = stele.search("tip", consumer_scope="project:v17", lifecycle_tiers=["hot"])
    assert {h["id"] for h in hits} == {hot}
    assert hits[0]["lifecycle_tier"] == "hot"


def test_revoke_by_key_and_unrevoke(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="tepa", now=TS)
    a = stele.add(_entry("Old host", key="pref:host"), ts=TS)["id"]
    b = stele.add(_entry("New host", key="pref:host", pinned=True), ts=TS)["id"]
    stele.promote(a, EV, actor="ci", ts=TS)
    stele.promote(b, EV, actor="ci", ts=TS)
    rev = stele.revoke_by_key("pref:host", evidence=EV, actor="ops", ts=TS, keep_id=b)
    assert a in rev["revoked"]
    assert rev["kept"] == b
    hits = stele.search("host", consumer_scope="project:v17")
    assert {h["id"] for h in hits} == {b}
    stele.unrevoke(a, evidence=EV, actor="ops", ts=TS)
    hits2 = stele.search("host", consumer_scope="project:v17")
    assert a in {h["id"] for h in hits2}


def test_pack_seal_and_explain(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="pack", now=TS)
    eid = stele.add(_entry("Seal tip", pinned=True), ts=TS)["id"]
    stele.promote(eid, EV, actor="ci", ts=TS)
    pack = tmp_path / "pack"
    stele.export(
        pack,
        scope="project:v17",
        audience="practitioner",
        purpose="test",
        created_at=TS,
        expiry="2099-01-01T00:00:00Z",
        entry_ids=[eid],
    )
    seal = stele.pack_seal(pack)
    assert stele.verify_pack_seal(pack, seal)["ok"] is True
    (pack / "entries" / f"{eid}.json").write_text('{"id":"tampered"}\n', encoding="utf-8")
    assert stele.verify_pack_seal(pack, seal)["ok"] is False
    explained = stele.search_explain("Seal tip", consumer_scope="project:v17")
    assert explained and "rank_detail" in explained[0]


def test_tepa_amvl_shaped_report(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="harness", now=TS)
    report = tepa_amvl_shaped_report(stele, consumer_scope="project:demo", now=TS)
    assert report["suite"] == "tepa_amvl_shaped"
    assert report["ok"] is True
