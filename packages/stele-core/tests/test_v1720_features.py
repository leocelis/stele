"""v17.2: DeLoRA + MELoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, dlr_meo_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_dlr_meo(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v172", now=TS)
    report = dlr_meo_shaped_report(
        stele, consumer_scope="project:v172", now=TS
    )
    assert report["suite"] == "dlr_meo_shaped"
    assert report["ok"] is True

    robust = stele.dlr_robust(hyperparam_robust=False)
    assert robust["apply"] is False

    rank = stele.meo_rank(higher_effective_rank=False)
    assert rank["apply"] is False
