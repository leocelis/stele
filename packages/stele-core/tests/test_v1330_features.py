"""v13.3: P-Tuning v2 + Prompt Tuning."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, ptv_ptl_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_ptv_ptl(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v133", now=TS)
    report = ptv_ptl_shaped_report(
        stele, consumer_scope="project:v133", now=TS
    )
    assert report["suite"] == "ptv_ptl_shaped"
    assert report["ok"] is True

    univ = stele.ptv_universal(match_finetune=False)
    assert univ["apply"] is False

    input_only = stele.ptl_input_only(input_layer_only=False)
    assert input_only["apply"] is False
