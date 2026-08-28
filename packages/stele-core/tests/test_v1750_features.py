"""v17.5: LoRA.rar + SVFT."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, lrr_svf_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_lrr_svf(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v175", now=TS)
    report = lrr_svf_shaped_report(
        stele, consumer_scope="project:v175", now=TS
    )
    assert report["suite"] == "lrr_svf_shaped"
    assert report["ok"] is True

    fast = stele.lrr_fast(realtime_merge=False)
    assert fast["apply"] is False

    geom = stele.svf_geom(weight_dependent=False)
    assert geom["apply"] is False
