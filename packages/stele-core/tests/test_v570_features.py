"""v5.7: Hindsight four-networks + ReasoningBank strategies/MaTTS."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, hindsight_reasoningbank_shaped_report

TS = "2026-08-23T03:00:00Z"


def test_hindsight_reasoningbank(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v57", now=TS)
    report = hindsight_reasoningbank_shaped_report(
        stele, consumer_scope="project:v57", now=TS
    )
    assert report["suite"] == "hindsight_reasoningbank_shaped"
    assert report["ok"] is True

    matts = stele.matts_contrastive_plan(mode="sequential", n_trajectories=2)
    assert matts["apply"] is False
    assert len(matts["steps"]) >= 3
