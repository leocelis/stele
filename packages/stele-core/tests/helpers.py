"""Shared test helpers (importable under pytest pythonpath)."""

from __future__ import annotations

from typing import Any

TS = "2026-08-20T12:00:00Z"


def base_entry(**overrides: Any) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "layer": "failure_lesson",
        "title": "Pin cache keys to calendar buckets",
        "body": "Day-scoped cache keys prevent stale cross-day reads after midnight rollover.",
        "scope": "project:demo",
        "temporal": {"valid_from": TS, "last_verified": TS},
        "provenance": {
            "agent": "agent-a",
            "task": "cache-fix",
            "environment": "local",
            "subject_id": "subj-demo",
            "source": "session:abc",
            "written_at": TS,
        },
    }
    # Deep-merge provenance if provided
    prov = overrides.pop("provenance", None)
    entry.update(overrides)
    if prov is not None:
        entry["provenance"] = prov
    return entry


def oracle_evidence(*, issuer: str = "ci-oracle") -> list[dict[str, Any]]:
    return [
        {
            "type": "test_result",
            "issuer": issuer,
            "ref": "tests/test_cache.py::test_day_bucket",
            "observed_at": TS,
            "verdict": "supports",
            "command": "pytest -q tests/test_cache.py",
            "exit_status": 0,
        }
    ]
