"""v15.1: SHiRA + WaveFT."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, shr_wft_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_shr_wft(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v151", now=TS)
    report = shr_wft_shaped_report(
        stele, consumer_scope="project:v151", now=TS
    )
    assert report["suite"] == "shr_wft_shaped"
    assert report["ok"] is True

    fusion = stele.shr_fusion(less_concept_loss=False)
    assert fusion["apply"] is False

    granular = stele.wft_granular(below_lora_min=False)
    assert granular["apply"] is False
