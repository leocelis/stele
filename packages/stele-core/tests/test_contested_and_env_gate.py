"""Contested resolution UX + workflow env-gate harness (FF-4, TECH_SPEC Q5)."""

from __future__ import annotations

from pathlib import Path

import pytest

from helpers import TS, base_entry, oracle_evidence
from stele_core import SchemaError, Stele, compare_with_without, workflow_env_gate_suite


def _promote_pair(stele: Stele) -> tuple[str, str]:
    """Two promoted lessons with contradictory evidence → REFLECT marks contested."""
    a = stele.add(
        base_entry(
            title="Cache bucket strategy alpha",
            body="Always pin cache keys to calendar day buckets.",
            provenance={
                "agent": "agent-a",
                "task": "t",
                "environment": "e",
                "subject_id": "s1",
                "source": "session:1",
                "written_at": TS,
            },
        ),
        ts=TS,
    )["id"]
    b = stele.add(
        base_entry(
            title="Cache bucket strategy beta",
            body="Never pin cache keys to calendar day buckets.",
            provenance={
                "agent": "agent-b",
                "task": "t",
                "environment": "e",
                "subject_id": "s2",
                "source": "session:2",
                "written_at": TS,
            },
        ),
        ts=TS,
    )["id"]
    stele.promote(
        a,
        [
            {
                "type": "test_result",
                "issuer": "ci-a",
                "ref": "tests/a.py",
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
                "ref": "prod-log",
                "observed_at": TS,
                "verdict": "refutes",
            }
        ],
        actor="ci-b",
        ts=TS,
    )
    report = stele.reflect(actor="maint", ts=TS, similarity_threshold=0.4)
    assert report["conflicts"], report
    return a, b


def test_list_and_resolve_contested(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="c", now=TS)
    a, b = _promote_pair(stele)

    contested = stele.list_contested()
    ids = {c["id"] for c in contested}
    assert a in ids and b in ids
    assert b in next(c["contested_with"] for c in contested if c["id"] == a)

    # Default search hides contested
    assert stele.search("cache bucket", consumer_scope="project:demo") == []
    # Explicit include still returns contested slices
    assert stele.search(
        "cache bucket", consumer_scope="project:demo", include_contested=True
    )

    # Authors cannot resolve their own fight
    with pytest.raises(SchemaError, match="cannot resolve"):
        stele.resolve_contested(
            winner_id=a,
            loser_id=b,
            evidence=oracle_evidence(issuer="agent-a"),
            actor="agent-a",
            ts=TS,
        )

    result = stele.resolve_contested(
        winner_id=a,
        loser_id=b,
        evidence=[
            {
                "type": "human_signoff",
                "issuer": "oracle-board",
                "ref": "design-review",
                "observed_at": TS,
                "verdict": "supports",
            }
        ],
        actor="oracle-board",
        ts=TS,
    )
    assert result["winner_state"] == "promoted"
    assert result["loser_state"] == "superseded"
    assert stele.list_contested() == []

    hits = stele.search("cache bucket", consumer_scope="project:demo")
    assert [h["id"] for h in hits] == [a]
    assert stele.store.read_entry(b)["state"] == "superseded"


def test_resolve_requires_support_verdict(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="c2", now=TS)
    a, b = _promote_pair(stele)
    with pytest.raises(SchemaError, match="supports"):
        stele.resolve_contested(
            winner_id=a,
            loser_id=b,
            evidence=[
                {
                    "type": "human_signoff",
                    "issuer": "board",
                    "ref": "nope",
                    "observed_at": TS,
                    "verdict": "refutes",
                }
            ],
            actor="board",
            ts=TS,
        )


def test_workflow_env_gate_suite(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="envgate", now=TS)
    eid = stele.add(
        base_entry(
            layer="workflow",
            title="Rotate cache keys workflow",
            body="Pin keys to calendar day buckets after deploy.",
            env_assumptions=["linux", "redis>=7"],
        ),
        ts=TS,
    )["id"]
    stele.promote(eid, oracle_evidence(), actor="ci", ts=TS)

    report = compare_with_without(workflow_env_gate_suite(), stele)
    by_id = {t["task_id"]: t for t in report["tasks"]}
    assert by_id["workflow-env-match"]["with_stele"] is True
    assert by_id["workflow-env-match"]["memory_helped"] is True
    # Mismatch: lesson is found but env gate fails the task
    assert by_id["workflow-env-mismatch"]["with_stele"] is False
    assert by_id["workflow-env-mismatch"]["env_gated"] is True
    assert report["without_stele_rate"] == 0.0
    assert report["lift"] == 0.5
