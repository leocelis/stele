"""v1.3: principal_scopes, forget_compliance, gatemem_shaped_report."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, gatemem_shaped_report

TS = "2026-08-20T20:00:00Z"


def _entry(
    title: str,
    *,
    scope: str = "project:v13",
    subject_id: str = "subj-v13",
    body: str = "Day-scoped keys prevent stale cross-day reads after midnight.",
) -> dict:
    return {
        "layer": "failure_lesson",
        "title": title,
        "body": body,
        "scope": scope,
        "temporal": {"valid_from": TS, "last_verified": TS},
        "provenance": {
            "agent": "good-agent",
            "task": "cache",
            "environment": "local",
            "subject_id": subject_id,
            "source": "session:ok",
            "written_at": TS,
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


def test_principal_scopes_blocks_foreign(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="a", now=TS)
    mine = stele.add(_entry("Mine day tip", scope="project:v13"), ts=TS)
    foreign = stele.add(_entry("Foreign day tip", scope="project:other"), ts=TS)
    _promote(stele, mine["id"])
    _promote(stele, foreign["id"])
    hits = stele.search(
        "day tip",
        consumer_scope="project:v13",
        principal_scopes=["project:v13"],
    )
    ids = {h["id"] for h in hits}
    assert mine["id"] in ids
    assert foreign["id"] not in ids
    assert all(h["scope"] == "project:v13" for h in hits)


def test_forget_compliance_after_subject_delete(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="f", now=TS)
    marker = "UNIQUE_FORGET_PROBE_V13"
    eid = stele.add(
        _entry("Secret tip", subject_id="subj-forget", body=f"{marker} body"),
        ts=TS,
    )["id"]
    _promote(stele, eid)
    stele.delete(subject_id="subj-forget", actor="ops", ts=TS)
    report = stele.forget_compliance(
        consumer_scope="project:v13",
        subject_id="subj-forget",
        entry_ids=[eid],
        probe_query=marker,
        forbidden_substrings=[marker],
    )
    assert report["ok"] is True
    assert report["store_clear"] is True
    assert report["search_leaks"] == []


def test_gatemem_shaped_report(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="g", now=TS)
    tip = stele.add(_entry("Day bucket tip", scope="project:demo"), ts=TS)
    _promote(stele, tip["id"])
    report = gatemem_shaped_report(stele, consumer_scope="project:demo", now=TS)
    assert report["suite"] == "gatemem_shaped"
    assert report["access_control"]["ok"] is True
    assert report["active_forgetting"]["ok"] is True
    assert report["ok"] is True
