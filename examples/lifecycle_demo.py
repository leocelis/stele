#!/usr/bin/env python3
"""Deterministic lifecycle demo — ADD → promote → search → export → delete."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from stele_core import Stele

TS = "2026-08-20T12:00:00Z"


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "store"
        stele = Stele.open(root, store_id="demo", now=TS)
        added = stele.add(
            {
                "layer": "failure_lesson",
                "title": "Pin cache keys to calendar buckets",
                "body": "Day-scoped keys prevent stale cross-day reads.",
                "scope": "project:demo",
                "temporal": {"valid_from": TS, "last_verified": TS},
                "provenance": {
                    "agent": "demo-agent",
                    "task": "cache-fix",
                    "environment": "local",
                    "subject_id": "subj-demo",
                    "source": "session:demo",
                    "written_at": TS,
                },
            },
            ts=TS,
        )
        print("ADD", json.dumps(added, sort_keys=True))

        promoted = stele.promote(
            added["id"],
            [
                {
                    "type": "test_result",
                    "issuer": "ci",
                    "ref": "tests/test_cache.py",
                    "observed_at": TS,
                    "verdict": "supports",
                    "command": "pytest -q",
                    "exit_status": 0,
                }
            ],
            actor="ci",
            ts=TS,
        )
        print("PROMOTE", json.dumps(promoted, sort_keys=True))

        hits = stele.search("cache buckets", consumer_scope="project:demo")
        print("SEARCH", json.dumps([{"id": h["id"], "title": h["title"]} for h in hits], sort_keys=True))

        pack = Path(tmp) / "pack"
        manifest = stele.export(
            pack,
            scope="project:demo",
            audience="expert",
            purpose="demo",
            created_at=TS,
            expiry="2027-01-01T00:00:00Z",
        )
        print("EXPORT", json.dumps({"entry_count": manifest["entry_count"]}, sort_keys=True))

        deleted = stele.delete(subject_id="subj-demo", actor="demo", ts=TS)
        print("DELETE", json.dumps(deleted, sort_keys=True))


if __name__ == "__main__":
    main()
