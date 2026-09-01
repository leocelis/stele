"""v13.8: BitFit + DoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, bft_dora_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_bft_dora(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v138", now=TS)
    report = bft_dora_shaped_report(
        stele, consumer_scope="project:v138", now=TS
    )
    assert report["suite"] == "bft_dora_shaped"
    assert report["ok"] is True

    tiny = stele.bft_tiny(fraction_pct=0)
    assert tiny["apply"] is False

    vs = stele.dora_vs_lora(closes_gap=False)
    assert vs["apply"] is False
