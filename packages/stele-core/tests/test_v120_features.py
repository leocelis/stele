"""v1.2: entangled suspects, hygiene candidates, prefer_fresh, governance report."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, governance_shaped_report

TS = "2026-08-20T18:00:00Z"
OLD = "2026-01-01T00:00:00Z"


def _entry(
    title: str,
    *,
    source: str = "session:ok",
    agent: str = "good-agent",
    last_verified: str = TS,
) -> dict:
    return {
        "layer": "failure_lesson",
        "title": title,
        "body": "Day-scoped keys prevent stale cross-day reads after midnight.",
        "scope": "project:v12",
        "temporal": {"valid_from": last_verified, "last_verified": last_verified},
        "provenance": {
            "agent": agent,
            "task": "cache",
            "environment": "local",
            "subject_id": "subj-v12",
            "source": source,
            "written_at": last_verified,
        },
    }


def _promote(stele: Stele, eid: str) -> None:
    stele.promote(
        eid,
        [
            {
                "type": "test_result",
                "issuer": "ci",
                "ref": "t",
                "observed_at": TS,
                "verdict": "supports",
                "command": "pytest -q",
                "exit_status": 0,
            }
        ],
        actor="ci",
        ts=TS,
    )


def test_entangled_suspects_via_link(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="e", now=TS)
    poison = stele.add(_entry("Poison", source="web_page:evil"), ts=TS)
    trusted = stele.add(_entry("Trusted entangled tip"), ts=TS)
    _promote(stele, poison["id"])
    _promote(stele, trusted["id"])
    stele.link(trusted["id"], kind="entry", ref=poison["id"], actor="ops", ts=TS)

    report = stele.entangled_suspects(untrusted_sources=["web_page"])
    assert poison["id"] in report["seeds"]
    assert report["count"] >= 1
    ids = {s["id"] for s in report["suspects"]}
    assert trusted["id"] in ids
    assert poison["id"] not in ids


def test_hygiene_net_harmful(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="h", now=TS)
    eid = stele.add(_entry("Bad tip"), ts=TS)["id"]
    _promote(stele, eid)
    stele.record_outcome(eid, "harmful", actor="ops", ts=TS)
    stele.record_outcome(eid, "harmful", actor="ops", ts=TS)
    out = stele.hygiene_candidates(now=TS)
    assert out["count"] >= 1
    assert any(c["id"] == eid and "net_harmful" in c["reasons"] for c in out["candidates"])


def test_prefer_fresh_orders_newer_first(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="f", now=TS)
    old = stele.add(_entry("Old day tip"), ts=TS)
    new = stele.add(_entry("New day tip"), ts=TS)
    _promote(stele, old["id"])
    _promote(stele, new["id"])
    later = "2026-08-21T12:00:00Z"
    stele.reverify(
        [new["id"]],
        [
            {
                "type": "test_result",
                "issuer": "ci",
                "ref": "t2",
                "observed_at": later,
                "verdict": "supports",
                "command": "pytest -q",
                "exit_status": 0,
            }
        ],
        actor="ci",
        ts=later,
    )
    hits = stele.search(
        "day tip",
        consumer_scope="project:v12",
        prefer_helpful=False,
        prefer_fresh=True,
    )
    ids = [h["id"] for h in hits]
    assert new["id"] in ids and old["id"] in ids
    assert ids.index(new["id"]) < ids.index(old["id"])


def test_governance_shaped_report(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="g", now=TS)
    stele.add(_entry("Normal tip"), ts=TS)
    report = governance_shaped_report(stele)
    assert report["suite"] == "governance_shaped"
    assert report["integrity_ok"] is True
    assert "note" in report
