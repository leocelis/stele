"""v1.4: lineage, belief_at, conflict_surface, memoryagent_shaped_report."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, memoryagent_shaped_report

TS = "2026-08-20T21:00:00Z"
T0 = "2026-08-19T12:00:00Z"


def _entry(
    title: str,
    *,
    body: str = "Day-scoped keys prevent stale cross-day reads after midnight.",
    scope: str = "project:v14",
    subject_id: str = "subj-v14",
    written_at: str = TS,
) -> dict:
    return {
        "layer": "failure_lesson",
        "title": title,
        "body": body,
        "scope": scope,
        "temporal": {"valid_from": written_at, "last_verified": written_at},
        "provenance": {
            "agent": "good-agent",
            "task": "cache",
            "environment": "local",
            "subject_id": subject_id,
            "source": "session:ok",
            "written_at": written_at,
        },
    }


def _promote(stele: Stele, eid: str, *, ts: str = TS) -> None:
    stele.promote(
        eid,
        [
            {
                "type": "test_result",
                "issuer": "ci",
                "ref": "t",
                "observed_at": ts,
                "verdict": "supports",
                "command": "pytest -q",
                "exit_status": 0,
            }
        ],
        actor="ci",
        ts=ts,
    )


def test_lineage_and_belief_at_after_supersede(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="l", now=TS)
    old = stele.add(_entry("Old day tip", written_at=T0), ts=T0)
    _promote(stele, old["id"], ts=T0)
    out = stele.supersede(
        old["id"],
        _entry("New day tip", written_at=TS),
        actor="ops",
        ts=TS,
    )
    _promote(stele, out["new_id"], ts=TS)

    lin = stele.lineage(old["id"])
    assert lin["state"] == "superseded"
    assert any(s["id"] == out["new_id"] for s in lin["successors"])
    assert lin["journal"]

    past = stele.belief_at(T0, consumer_scope="project:v14", query="day tip")
    assert past["mode"] == "search"
    assert any(s["id"] == old["id"] for s in past["slices"])

    inv = stele.belief_at(T0, consumer_scope="project:v14")
    assert inv["mode"] == "inventory"
    assert any(b["id"] == old["id"] for b in inv["beliefs"])


def test_conflict_surface_preserves_pairs(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="c", now=TS)
    a = stele.add(
        _entry(
            "Cache bucket strategy alpha",
            body="Always pin cache keys to calendar day buckets.",
            subject_id="s1",
        ),
        ts=TS,
    )["id"]
    b = stele.add(
        _entry(
            "Cache bucket strategy beta",
            body="Never pin cache keys to calendar day buckets.",
            subject_id="s2",
        ),
        ts=TS,
    )["id"]
    stele.promote(
        a,
        [
            {
                "type": "test_result",
                "issuer": "ci-a",
                "ref": "a",
                "observed_at": TS,
                "verdict": "supports",
                "command": "pytest -q",
                "exit_status": 0,
            }
        ],
        actor="ci-a",
        ts=TS,
    )
    stele.promote(
        b,
        [
            {
                "type": "env_feedback",
                "issuer": "ci-b",
                "ref": "log",
                "observed_at": TS,
                "verdict": "refutes",
            }
        ],
        actor="ci-b",
        ts=TS,
    )
    stele.reflect(actor="maint", ts=TS, similarity_threshold=0.4)
    surface = stele.conflict_surface()
    assert surface["count"] >= 1
    assert all(p.get("preserved") is True for p in surface["conflicts"])


def test_memoryagent_shaped_report(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="m", now=TS)
    report = memoryagent_shaped_report(stele, consumer_scope="project:demo", now=TS)
    assert report["suite"] == "memoryagent_shaped"
    assert report["accurate_retrieval"]["ok"] is True
    assert report["selective_forgetting"]["ok"] is True
    assert report["lineage_audit"]["ok"] is True
    assert report["ok"] is True
