"""v11.9: Multimodal-CoT + Maieutic Prompting."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, mmcot_mai_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_mmcot_mai(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v119", now=TS)
    report = mmcot_mai_shaped_report(
        stele, consumer_scope="project:v119", now=TS
    )
    assert report["suite"] == "mmcot_mai_shaped"
    assert report["ok"] is True

    sep = stele.mmcot_separate(two_stage=False)
    assert sep["apply"] is False

    unr = stele.mai_unreliable(tolerate=False)
    assert unr["apply"] is False
