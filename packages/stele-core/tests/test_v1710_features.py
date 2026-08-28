"""v17.1: SwitchLoRA + Chain of LoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, swl_col_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_swl_col(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v171", now=TS)
    report = swl_col_shaped_report(
        stele, consumer_scope="project:v171", now=TS
    )
    assert report["suite"] == "swl_col_shaped"
    assert report["ok"] is True

    full = stele.swl_full(mimics_fullrank=False)
    assert full["apply"] is False

    gap = stele.col_gap(closes_ft_gap=False)
    assert gap["apply"] is False
