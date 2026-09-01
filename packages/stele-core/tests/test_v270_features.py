"""v2.7: TARL five-action updates + Memory Worth."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, tarl_mw_shaped_report

TS = "2026-08-21T00:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v27",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def test_tarl_and_memory_worth(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="tarl", now=TS)
    base = {
        "layer": "failure_lesson",
        "title": "Retry tip",
        "body": "Retry the flaky HTTP client at most three times with backoff.",
        "scope": "project:v27",
        "conflict_key": "cfg:retry",
        "temporal": {"valid_from": TS, "last_verified": TS},
        "provenance": {
            "agent": "oracle",
            "task": "t",
            "environment": "local",
            "subject_id": "s",
            "source": "ci:gate",
            "written_at": TS,
        },
    }
    eid = stele.add(base, ts=TS)["id"]
    stele.promote(eid, EV, actor="ci", ts=TS)
    assert stele.propose_update(base)["action"] == "noop"

    weak = dict(base)
    weak["body"] = "Retry the flaky HTTP client at most one time with backoff."
    weak["provenance"] = {
        **base["provenance"],
        "agent": "pack-hydrate",
        "source": "pack:x",
    }
    rejected = stele.apply_update(weak, actor="ci", ts=TS)
    assert rejected["action"] == "reject_conflict"
    assert rejected["state"] == "revoked"

    strong = dict(base)
    strong["body"] = "Retry the flaky HTTP client at most five times with backoff."
    strong["provenance"] = {**base["provenance"], "source": "oracle:gate"}
    revised = stele.apply_update(strong, actor="ci", ts=TS)
    assert revised["action"] == "revise"
    stele.promote(revised["id"], EV, actor="ci", ts=TS)

    led = stele.ledger_view()
    assert led["counts"]["accepted"] >= 1
    assert led["counts"]["rejected"] >= 1

    tip = revised["id"]
    stele.record_outcome(tip, "helpful", actor="ci", ts=TS)
    stele.record_outcome(tip, "harmful", actor="ci", ts=TS)
    stele.record_outcome(tip, "harmful", actor="ci", ts=TS)
    mw = stele.memory_worth(tip)
    assert mw["known"] is True
    assert mw["mw"] == round(1 / 3, 6)
    low = stele.low_worth_scan(threshold=0.5, min_samples=2)
    assert tip in {x["id"] for x in low["low"]}
    hits = stele.search(
        "retry",
        consumer_scope="project:v27",
        min_worth=0.5,
        worth_min_samples=2,
        worth_unknown_ok=False,
    )
    assert tip not in {h["id"] for h in hits}


def test_tarl_mw_shaped_report(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="harness", now=TS)
    report = tarl_mw_shaped_report(
        stele, consumer_scope="project:demo", now=TS
    )
    assert report["suite"] == "tarl_mw_shaped"
    assert report["ok"] is True
