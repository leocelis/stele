"""v13.6: LoRA + AdapterFusion."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, lora_adf_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_lora_adf(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v136", now=TS)
    report = lora_adf_shaped_report(
        stele, consumer_scope="project:v136", now=TS
    )
    assert report["suite"] == "lora_adf_shaped"
    assert report["ok"] is True

    lat = stele.lora_latency(zero_extra=False)
    assert lat["apply"] is False

    nd = stele.adf_nondestruct(nondestructive=False)
    assert nd["apply"] is False
