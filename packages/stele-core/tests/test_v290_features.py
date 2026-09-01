"""v2.9: LatticeMind symbolic conflicts + Cordon effect outbox."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, lattice_cordon_shaped_report

TS = "2026-08-21T00:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v29",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def test_lattice_and_cordon(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="lat", now=TS)

    def add(title: str, body: str, key: str) -> str:
        eid = stele.add(
            {
                "layer": "failure_lesson",
                "title": title,
                "body": body,
                "scope": "project:v29",
                "conflict_key": key,
                "temporal": {"valid_from": TS, "last_verified": TS},
                "provenance": {
                    "agent": "a",
                    "task": "t",
                    "environment": "local",
                    "subject_id": "s",
                    "source": "ci:x",
                    "written_at": TS,
                },
            },
            ts=TS,
        )["id"]
        stele.promote(eid, EV, actor="ci", ts=TS)
        return eid

    a = add("Rate limit A", "Cap API clients at 10 requests per second.", "cfg:rps")
    b = add("Rate limit B", "Cap API clients at 100 requests per second.", "cfg:rps")
    assert stele.symbolic_conflict_scan()["count_key_conflicts"] >= 1
    assert stele.classify_conflict(a, b)["kind"] == "credibility"
    compact = stele.compact_render(
        "rate", consumer_scope="project:v29", reader_budget=80
    )
    assert compact["count"] >= 1
    assert compact["used"] <= 80

    fx = stele.stage_effect(
        sink="pager.notify",
        payload={"sev": 1},
        actor="ci",
        ts=TS,
        belief_ids=[a],
    )
    assert fx["state"] == "pending"
    assert stele.release_effects(effect_ids=[fx["effect_id"]])["count"] == 1
    stele.mark_effect_dispatched(fx["effect_id"], receipt="r1")
    assert stele.list_effects(state="dispatched")["count"] >= 1


def test_lattice_cordon_shaped_report(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="harness", now=TS)
    report = lattice_cordon_shaped_report(
        stele, consumer_scope="project:demo", now=TS
    )
    assert report["suite"] == "lattice_cordon_shaped"
    assert report["ok"] is True
