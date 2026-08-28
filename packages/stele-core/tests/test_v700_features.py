"""v7.0: ECHO + Agent0."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, echomem_agent0_shaped_report

TS = "2026-08-23T16:00:00Z"


def test_echomem_agent0(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v70", now=TS)
    report = echomem_agent0_shaped_report(
        stele, consumer_scope="project:v70", now=TS
    )
    assert report["suite"] == "echomem_agent0_shaped"
    assert report["ok"] is True

    bad = stele.curriculum_reward(
        r_uncertainty=1.0, r_tool=1.0, format_ok=False
    )
    assert float(bad["r_curriculum"]) == 0.0
