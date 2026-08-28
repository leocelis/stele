"""v6.9: Absolute Zero + R-Zero."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, abszero_rzero_shaped_report

TS = "2026-08-23T15:00:00Z"


def test_abszero_rzero(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v69", now=TS)
    report = abszero_rzero_shaped_report(
        stele, consumer_scope="project:v69", now=TS
    )
    assert report["suite"] == "abszero_rzero_shaped"
    assert report["ok"] is True

    z = stele.learnability_reward(mean_solve_rate=0.0)
    assert float(z["r_propose"]) == 0.0
    u = stele.uncertainty_reward(empirical_accuracy=1.0)
    assert float(u["r_uncertainty"]) == 0.0
