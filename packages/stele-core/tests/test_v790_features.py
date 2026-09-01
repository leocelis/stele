"""v7.9: CMA + AgentFold."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, cma_agentfold_shaped_report

TS = "2026-08-24T01:00:00Z"


def test_cma_agentfold(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v79", now=TS)
    report = cma_agentfold_shaped_report(
        stele, consumer_scope="project:v79", now=TS
    )
    assert report["suite"] == "cma_agentfold_shaped"
    assert report["ok"] is True

    drop = stele.cma_selective_retain(utility=0.1, retain_threshold=0.4)
    assert drop["retain"] is False

    over = stele.agentfold_context_budget(
        turns=100, tokens=8000, soft_cap=7000
    )
    assert over["under_cap"] is False
