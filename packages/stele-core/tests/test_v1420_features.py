"""v14.2: Tied-LoRA + LoRA+."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, tlo_lrp_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_tlo_lrp(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v142", now=TS)
    report = tlo_lrp_shaped_report(
        stele, consumer_scope="project:v142", now=TS
    )
    assert report["suite"] == "tlo_lrp_shaped"
    assert report["ok"] is True

    efficient = stele.tlo_efficient(weight_tied=False)
    assert efficient["apply"] is False

    speed = stele.lrp_speed(faster_than_lora=False)
    assert speed["apply"] is False
