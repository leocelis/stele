"""v6.3: Trace2Skill + Evo-Memory."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, trace2skill_evomemory_shaped_report

TS = "2026-08-23T09:00:00Z"


def test_trace2skill_evomemory(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v63", now=TS)
    report = trace2skill_evomemory_shaped_report(
        stele, consumer_scope="project:v63", now=TS
    )
    assert report["suite"] == "trace2skill_evomemory_shaped"
    assert report["ok"] is True

    spe = stele.search_predict_evolve_check(["search", "predict", "evolve"])
    assert spe["valid"] is True
    gate = stele.skill_mode_gate(mode="create", has_human_skill=False)
    assert gate["allowed"] is True
