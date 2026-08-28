"""v7.3: SAMULE + LIVE-EVO."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, samule_liveevo_shaped_report

TS = "2026-08-23T19:00:00Z"


def test_samule_liveevo(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v73", now=TS)
    report = samule_liveevo_shaped_report(
        stele, consumer_scope="project:v73", now=TS
    )
    assert report["suite"] == "samule_liveevo_shaped"
    assert report["ok"] is True

    down = stele.update_experience_weight(
        weight=1.0, delta_on_minus_off=-0.5, lr=0.1
    )
    assert float(down["weight"]) == 0.95
    assert down["reinforced"] is False
