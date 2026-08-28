"""v7.1: MAE + SAGE multi-agent."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, mae_sagema_shaped_report

TS = "2026-08-23T17:00:00Z"


def test_mae_sagema(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v71", now=TS)
    report = mae_sagema_shaped_report(
        stele, consumer_scope="project:v71", now=TS
    )
    assert report["suite"] == "mae_sagema_shaped"
    assert report["ok"] is True

    easy = stele.mae_proposer_reward(
        quality_score=0.8, solver_failed=False, difficulty_weight=0.5
    )
    assert float(easy["r_proposer"]) == 0.4
