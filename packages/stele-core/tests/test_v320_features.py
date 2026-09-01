"""v3.2: MemoRepair min-cut + CUPMem adjudication + CMGL admit."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, memorepair_cupmem_cmgl_shaped_report

TS = "2026-08-21T00:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v32",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def test_mincut_cupmem_cmgl(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v32", now=TS)
    fault = stele.add(
        {
            "layer": "failure_lesson",
            "title": "Tool schema v1",
            "body": "Use tool schema version one for checkout.",
            "scope": "project:v32",
            "conflict_key": "tool:checkout",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "a",
                "task": "t",
                "environment": "local",
                "subject_id": "s",
                "source": "ci:a",
                "written_at": TS,
            },
            "usage": {"helpful": 1, "pinned": True},
        },
        ts=TS,
    )["id"]
    stele.promote(fault, EV, actor="ci", ts=TS)
    child = stele.add(
        {
            "layer": "failure_lesson",
            "title": "Checkout skill",
            "body": "Cached skill depending on tool schema version one.",
            "scope": "project:v32",
            "conflict_key": "skill:checkout",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "a",
                "task": "t2",
                "environment": "local",
                "subject_id": "s",
                "source": "ci:b",
                "written_at": TS,
            },
            "links": [{"kind": "entry", "ref": fault}],
            "usage": {"helpful": 4, "pinned": True},
        },
        ts=TS,
    )["id"]
    stele.promote(child, EV, actor="ci", ts=TS)

    plan = stele.repair_select_mincut(fault, lambda_cost=0.5)
    assert plan["method"] == "mincut"
    assert child in plan["selected"]

    adj = stele.adjudicate_update(
        {
            "title": "Tool schema v2",
            "body": "Use tool schema version two for checkout.",
            "conflict_key": "tool:checkout",
            "provenance": {"agent": "ci", "source": "ci:v2"},
            "evidence": EV,
        },
        evidence=EV,
    )
    assert adj["action"] in {"revise", "activate", "block", "unknown_current"}

    assert "count" in stele.unknown_current_slots()

    auth = stele.authorize_retrieval([fault, child])
    assert auth["authorized_count"] >= 1

    denied = stele.admit_gate(
        action="delete",
        actor="ci",
        authority_bundle={"natural_language_only": True, "actor": "ci"},
        ts=TS,
    )
    assert denied["admitted"] is False

    ok = stele.admit_gate(
        action="delete",
        actor="ci",
        authority_bundle={"roles": ["operator"], "actor": "ci"},
        entry_id=fault,
        ts=TS,
    )
    assert ok["admitted"] is True
    assert stele.verify_admit_receipt(ok["receipt"])["ok"] is True


def test_harness_v32(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "h", store_id="h", now=TS)
    report = memorepair_cupmem_cmgl_shaped_report(
        stele, consumer_scope="project:demo", now=TS
    )
    assert report["suite"] == "memorepair_cupmem_cmgl_shaped"
    assert report["ok"] is True
