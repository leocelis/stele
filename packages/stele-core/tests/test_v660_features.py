"""v6.6: ProcMEM + MemRL."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, procmem_memrl_shaped_report

TS = "2026-08-23T12:00:00Z"


def test_procmem_memrl(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v66", now=TS)
    report = procmem_memrl_shaped_report(
        stele, consumer_scope="project:v66", now=TS
    )
    assert report["suite"] == "procmem_memrl_shaped"
    assert report["ok"] is True

    w = stele.semantic_vs_utility_warn(similarity=0.2, utility=0.9)
    assert w["trap"] is False
    m = stele.skill_score_maintain(frequency=0, avg_gain=1.0)
    assert m["prune"] is True
