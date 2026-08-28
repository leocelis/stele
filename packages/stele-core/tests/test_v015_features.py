"""v0.1.5: judgment wire adapter, memory_arena_smoke, search overhead."""

from __future__ import annotations

from pathlib import Path

import pytest

from helpers import TS, base_entry, oracle_evidence
from stele_core import (
    SchemaError,
    Stele,
    judgment_entry,
    measure_search_overhead,
    memory_arena_smoke,
)


def test_judgment_entry_adds_and_promotes(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="j", now=TS)
    payload = judgment_entry(
        {
            "title": "Prefer explicit scope on SEARCH",
            "correction": "Cross-project reads must use scope_override, never default.",
            "layer": "decision",
            "scope": "project:demo",
            "rejected_options": ["silent cross-scope bleed"],
            "subject_id": "subj-j",
            "source": "judgment:codified-1",
        },
        written_at=TS,
    )
    assert payload["provenance"]["agent"] == "judgment-adapter"
    eid = stele.add(payload, ts=TS)["id"]
    stele.promote(eid, oracle_evidence(issuer="reviewer"), actor="reviewer", ts=TS)
    hits = stele.search("scope_override", consumer_scope="project:demo")
    assert any(h["id"] == eid for h in hits)


def test_judgment_rejects_private_paths() -> None:
    with pytest.raises(SchemaError, match="private-source"):
        judgment_entry(
            {
                "title": "x",
                "body": "y",
                "source": "ledger/tenants/private/secret",
            },
            written_at=TS,
        )


def test_memory_arena_smoke_and_overhead(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="arena", now=TS)
    eid = stele.add(
        base_entry(
            layer="workflow",
            title="Rotate cache keys by calendar day",
            body="Use day buckets when rotating cache keys on redis>=7 linux hosts.",
            env_assumptions=["linux", "redis>=7"],
        ),
        ts=TS,
    )["id"]
    stele.promote(eid, oracle_evidence(), actor="ci", ts=TS)

    arena = memory_arena_smoke(stele)
    assert arena["n"] == 3
    assert arena["with_stele_rate"] >= arena["without_stele_rate"]
    # env-match should help; env-mismatch must not count as success
    by_id = {r["task_id"]: r for r in arena["tasks"]}
    assert by_id["workflow-env-match"]["with_stele"] is True
    assert by_id["workflow-env-mismatch"]["with_stele"] is False

    cost = measure_search_overhead(stele, rounds=20)
    assert cost["hit_count"] >= 1
    assert cost["with_search_median_ms"] >= 0.0
    assert "overhead_median_ms" in cost
