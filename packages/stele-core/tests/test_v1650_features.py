"""v16.5: LoraHub + MultiLoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, lhb_mlr_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_lhb_mlr(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v165", now=TS)
    report = lhb_mlr_shaped_report(
        stele, consumer_scope="project:v165", now=TS
    )
    assert report["suite"] == "lhb_mlr_shaped"
    assert report["ok"] is True

    nograd = stele.lhb_nograd(gradient_free=False)
    assert nograd["apply"] is False

    demo = stele.mlr_demo(more_democratic=False)
    assert demo["apply"] is False
