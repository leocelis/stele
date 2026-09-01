"""v2.0: health_report, release_gate, cue_tags, derived SQLite index."""

from __future__ import annotations

from pathlib import Path

import pytest

from stele_core import Stele, SchemaError, gpm_release_shaped_report

TS = "2026-08-21T00:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v20",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def _entry(title: str, *, cues: list[str] | None = None) -> dict:
    e = {
        "layer": "failure_lesson",
        "title": title,
        "body": f"{title} body with enough tokens for health and cue tests.",
        "scope": "project:v20",
        "temporal": {"valid_from": TS, "last_verified": TS},
        "provenance": {
            "agent": "agent",
            "task": "t",
            "environment": "local",
            "subject_id": "subj-v20",
            "source": "session:ok",
            "written_at": TS,
        },
    }
    if cues:
        e["cue_tags"] = cues
    return e


def test_health_and_release_gate(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="health", now=TS)
    eid = stele.add(_entry("Health tip"), ts=TS)["id"]
    stele.promote(eid, EV, actor="ci", ts=TS)
    health = stele.health_report(now=TS)
    assert health["ok"] is True
    gate = stele.release_gate(now=TS)
    assert gate["released"] is True
    bad = stele.release_gate(expected_head="deadbeef", now=TS)
    assert bad["ok"] is False
    assert "head_mismatch" in bad["barriers"]


def test_cues_and_sqlite(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="cue", now=TS)
    a = stele.add(_entry("Day tip", cues=["day-bucket", "clock"]), ts=TS)["id"]
    b = stele.add(_entry("Other tip", cues=["network"]), ts=TS)["id"]
    stele.promote(a, EV, actor="ci", ts=TS)
    stele.promote(b, EV, actor="ci", ts=TS)
    hits = stele.search("tip", consumer_scope="project:v20", cue_tags=["day-bucket"])
    assert {h["id"] for h in hits} == {a}
    rebuilt = stele.rebuild_sqlite_index()
    assert rebuilt["entry_count"] == 2
    sq = stele.search_sqlite("Day", states=["promoted"], cue="day-bucket")
    assert any(r["id"] == a for r in sq)


def test_export_require_release(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="exp", now=TS)
    eid = stele.add(_entry("Pack tip"), ts=TS)["id"]
    stele.promote(eid, EV, actor="ci", ts=TS)
    pack = tmp_path / "pack"
    manifest = stele.export(
        pack,
        scope="project:v20",
        audience="practitioner",
        purpose="test",
        created_at=TS,
        expiry="2099-01-01T00:00:00Z",
        require_release=True,
    )
    assert manifest.get("release_ok") is True


def test_gpm_release_shaped_report(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="harness", now=TS)
    report = gpm_release_shaped_report(stele, consumer_scope="project:demo", now=TS)
    assert report["suite"] == "gpm_release_shaped"
    assert report["ok"] is True
