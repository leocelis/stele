"""v6.4: Mem-α + AgentHER."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, memalpha_agenther_shaped_report

TS = "2026-08-23T10:00:00Z"


def test_memalpha_agenther(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v64", now=TS)
    report = memalpha_agenther_shaped_report(
        stele, consumer_scope="project:v64", now=TS
    )
    assert report["suite"] == "memalpha_agenther_shaped"
    assert report["ok"] is True

    w = stele.memory_write_op(slot="core", op="update", content="summary")
    assert w["allowed"] is True
    j = stele.multi_judge_accept(confidence_j1=0.5, confidence_j2=0.9, theta=0.7)
    assert j["accepted"] is False
