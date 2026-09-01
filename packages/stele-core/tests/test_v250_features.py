"""v2.5: GitOfThoughts-shaped commits, diff, copyability gate."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, gitofthoughts_shaped_report

TS = "2026-08-21T00:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v25",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def _entry(title: str, body: str) -> dict:
    return {
        "layer": "failure_lesson",
        "title": title,
        "body": body,
        "scope": "project:v25",
        "temporal": {"valid_from": TS, "last_verified": TS},
        "provenance": {
            "agent": "a",
            "task": "t",
            "environment": "local",
            "subject_id": "s",
            "source": "session:ok",
            "written_at": TS,
        },
    }


def test_commits_diff_copyability(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="got", now=TS)
    a = stele.add(
        _entry("Alpha tip", "Alpha tip body with unique alpha tokens here."),
        ts=TS,
    )["id"]
    b = stele.add(
        _entry("Beta tip", "Beta tip body with unique beta tokens here."),
        ts=TS,
    )["id"]
    stele.promote(a, EV, actor="ci", ts=TS)
    stele.promote(b, EV, actor="ci", ts=TS)
    c1 = stele.commit_view("v1", entry_ids=[a], actor="ci", ts=TS, outcome="success")
    c2 = stele.commit_view(
        "v2", entry_ids=[a, b], actor="ci", ts=TS, branch="explore", outcome="failed"
    )
    ha, hb = c1["commit"]["commit_hash"], c2["commit"]["commit_hash"]
    assert stele.checkout_view(ha)["entry_ids"] == [a]
    diff = stele.diff_commits(ha, hb)
    assert b in diff["only_in_b"]
    assert stele.verify_commit_chain()["ok"] is True
    near = stele.copyability_gate(
        "Alpha tip body with unique alpha tokens here",
        consumer_scope="project:v25",
        threshold=0.4,
    )
    assert near["memory_likely_helps"] is True


def test_gitofthoughts_shaped_report(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="harness", now=TS)
    report = gitofthoughts_shaped_report(stele, consumer_scope="project:demo", now=TS)
    assert report["suite"] == "gitofthoughts_shaped"
    assert report["ok"] is True
