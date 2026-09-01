"""v4.0: Deterministic freshness + MemTxn patch/temporal + fleet propagation."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, freshness_memtxn_fleet_shaped_report

TS = "2026-08-21T00:00:00Z"
TS_OLD = "2026-08-01T00:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v40",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def test_freshness_memtxn_fleet(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v40", now=TS)
    old = stele.add(
        {
            "layer": "decision",
            "title": "Retry cap v1",
            "body": "Payment retries capped at three. version 1 serial_1.",
            "scope": "project:v40",
            "conflict_key": "policy:retry_cap",
            "temporal": {"valid_from": TS_OLD, "last_verified": TS_OLD},
            "provenance": {
                "agent": "oracle",
                "task": "old",
                "environment": "local",
                "subject_id": "s",
                "source": "oracle:gate",
                "written_at": TS_OLD,
            },
            "usage": {"helpful": 1, "harmful": 0},
        },
        ts=TS_OLD,
    )["id"]
    stele.promote(old, EV, actor="ci", ts=TS_OLD)
    new = stele.add(
        {
            "layer": "decision",
            "title": "Retry cap v2",
            "body": "Payment retries capped at five. version 2 serial_2.",
            "scope": "project:v40",
            "conflict_key": "policy:retry_cap",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "oracle",
                "task": "new",
                "environment": "local",
                "subject_id": "s",
                "source": "oracle:gate",
                "written_at": TS,
            },
            "usage": {"helpful": 2, "harmful": 0, "pinned": True},
        },
        ts=TS,
    )["id"]
    stele.promote(new, EV, actor="ci", ts=TS)

    assert stele.extract_version_markers(new)["max_serial"] == 2
    assert stele.freshness_resolve(conflict_key="policy:retry_cap")["winner"]["id"] == new
    assert any(
        r["id"] == new
        for r in stele.assemble_current("payment retries cap")["resolved"]
    )
    assert stele.hop_freshness(["payment retries"])["ok"] is True

    assert stele.patch_test(
        {"title": "x", "body": "Payment retries capped at five"},
        new,
        cited_span="capped at five",
    )["ok"]
    assert not stele.patch_test(
        {"title": "x", "body": "nope"},
        new,
        cited_span="launch the missiles",
    )["ok"]

    assert stele.temporal_resolve("policy:retry_cap")["visible"]["id"] == new
    assert (
        stele.recover_active_map(["policy:retry_cap"])["active"]["policy:retry_cap"][
            "id"
        ]
        == new
    )

    assert stele.fleet_scope_gate(new, allowed_scopes=["project:v40"])["ok"]
    assert not stele.fleet_scope_gate(new, allowed_scopes=["project:other"])["ok"]

    plan = stele.propagate_plan(
        source_scope="project:v40",
        target_scopes=["project:fleet-b"],
        query="payment",
    )
    assert plan["count"] >= 1

    stale = stele.stale_propagation_scan()
    assert any(s["id"] == old for s in stale["suspects"])


def test_harness_v40(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "h", store_id="h", now=TS)
    report = freshness_memtxn_fleet_shaped_report(
        stele, consumer_scope="project:demo", now=TS
    )
    assert report["suite"] == "freshness_memtxn_fleet_shaped"
    assert report["ok"] is True
