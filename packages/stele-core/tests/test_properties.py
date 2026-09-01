"""Property-style governance tests."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from stele_core import SchemaError, Stele

NOW = "2026-09-01T12:00:00Z"


@pytest.fixture
def stele() -> Stele:
    tmp = tempfile.mkdtemp()
    return Stele.open(Path(tmp) / "s", store_id="prop", now=NOW)


def _entry(task: str = "t1") -> dict:
    return {
        "layer": "failure_lesson",
        "title": "t",
        "body": "b",
        "scope": "project:p",
        "temporal": {"valid_from": NOW, "last_verified": NOW},
        "provenance": {
            "agent": "a",
            "task": task,
            "environment": "local",
            "subject_id": "s1",
            "source": f"session:{task}",
            "written_at": NOW,
        },
    }


def test_quarantined_never_in_search(stele: Stele) -> None:
    added = stele.add(_entry(), ts=NOW)
    assert added["state"] == "quarantined"
    assert stele.search("t", consumer_scope="project:p") == []


def test_self_evidence_promote_rejected(stele: Stele) -> None:
    added = stele.add(_entry("t2"), ts=NOW)
    with pytest.raises(SchemaError, match="self-issued"):
        stele.promote(
            added["id"],
            [
                {
                    "type": "test_result",
                    "issuer": "a",
                    "ref": "r",
                    "observed_at": NOW,
                    "verdict": "supports",
                }
            ],
            actor="ci",
            ts=NOW,
        )
