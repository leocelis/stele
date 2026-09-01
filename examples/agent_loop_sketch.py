"""Sketch: task → add → CI promote → search → act. No framework lock-in."""
from __future__ import annotations

import tempfile
from pathlib import Path

from stele_core import Stele

NOW = "2026-09-01T12:00:00Z"


def run_task(stele: Stele, task: str, scope: str) -> str:
    lesson = stele.add(
        {
            "layer": "failure_lesson",
            "title": f"Lesson from {task}",
            "body": "Always run doctor before deploy.",
            "scope": scope,
            "temporal": {"valid_from": NOW, "last_verified": NOW},
            "provenance": {
                "agent": "worker",
                "task": task,
                "environment": "ci",
                "subject_id": "team-1",
                "source": f"session:{task}",
                "written_at": NOW,
            },
        },
        ts=NOW,
    )
    stele.promote(
        lesson["id"],
        [
            {
                "type": "test_result",
                "issuer": "ci",
                "ref": "ci/pipeline",
                "observed_at": NOW,
                "verdict": "supports",
                "command": "make check",
                "exit_status": 0,
            }
        ],
        actor="ci",
        ts=NOW,
    )
    slices = stele.search("doctor deploy", consumer_scope=scope)
    if not slices:
        return ""
    entries = slices[0].get("entries") or []
    return str(entries[0].get("title", "")) if entries else ""


with tempfile.TemporaryDirectory() as tmp:
    s = Stele.open(Path(tmp) / "store", store_id="sketch", now=NOW)
    title = run_task(s, "deploy-api", "project:api")
    print("retrieved:", title)
