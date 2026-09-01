"""Minimal stele-core quickstart — no MCP. Run: python examples/quickstart_core.py"""
from __future__ import annotations

import tempfile
from pathlib import Path

from stele_core import Stele

NOW = "2026-09-01T12:00:00Z"
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp) / "store"
    s = Stele.open(root, store_id="quickstart", now=NOW)
    added = s.add(
        {
            "layer": "failure_lesson",
            "title": "Pin cache keys to calendar buckets",
            "body": "Day-scoped keys prevent stale cross-day reads.",
            "scope": "project:demo",
            "temporal": {"valid_from": NOW, "last_verified": NOW},
            "provenance": {
                "agent": "agent-a",
                "task": "cache-fix",
                "environment": "local",
                "subject_id": "subj-1",
                "source": "session:abc",
                "written_at": NOW,
            },
        }
    )
    assert added["state"] == "quarantined"
    s.promote(
        added["id"],
        [
            {
                "type": "test_result",
                "issuer": "ci",
                "ref": "tests/test_cache.py",
                "observed_at": NOW,
                "verdict": "supports",
                "command": "pytest -q",
                "exit_status": 0,
            }
        ],
        actor="ci",
        ts=NOW,
    )
    hits = s.search("cache buckets", consumer_scope="project:demo")
    assert hits
    print("quickstart_core OK", len(hits), "slice(s)")
