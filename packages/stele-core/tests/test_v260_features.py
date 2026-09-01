"""v2.6: ChronoMem version rollback + MemStrata supersession."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, chronomem_strata_shaped_report

TS = "2026-08-21T00:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v26",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def test_chrono_and_strata(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="chrono", now=TS)
    old = stele.add(
        {
            "layer": "failure_lesson",
            "title": "Port tip v1",
            "body": "Use port 8080 for the local API listener in development.",
            "scope": "project:v26",
            "conflict_key": "cfg:port",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "a",
                "task": "t",
                "environment": "local",
                "subject_id": "s",
                "source": "session:v1",
                "written_at": TS,
            },
        },
        ts=TS,
    )["id"]
    stele.promote(old, EV, actor="ci", ts=TS)
    pin = stele.pin_memory_version("v1", actor="ci", ts=TS)
    ver = pin["commit"]["commit_hash"]
    new = stele.supersede(
        old,
        {
            "layer": "failure_lesson",
            "title": "Port tip v2",
            "body": "Use port 9090 for the local API listener in development.",
            "scope": "project:v26",
            "conflict_key": "cfg:port",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "a",
                "task": "t",
                "environment": "local",
                "subject_id": "s",
                "source": "session:v2",
                "written_at": TS,
            },
        },
        actor="ci",
        ts=TS,
    )
    stele.promote(new["new_id"], EV, actor="ci", ts=TS)
    assert stele.stale_fact_scan()["count"] >= 1
    live = stele.search(
        "port", consumer_scope="project:v26", exclude_superseded=True
    )
    assert old not in {h["id"] for h in live}
    cf = stele.counterfactual_search(
        "port", consumer_scope="project:v26", version_commit=ver
    )
    assert old in {h["id"] for h in cf["hits"]}
    stele.activate_version(ver)
    assert old in {
        h["id"] for h in stele.search("port", consumer_scope="project:v26")
    }
    stele.activate_version(None)


def test_chronomem_strata_shaped_report(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="harness", now=TS)
    report = chronomem_strata_shaped_report(
        stele, consumer_scope="project:demo", now=TS
    )
    assert report["suite"] == "chronomem_strata_shaped"
    assert report["ok"] is True
