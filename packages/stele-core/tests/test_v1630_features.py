"""v16.3: HydraLoRA + LoRA-LEGO."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, hyd_llg_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_hyd_llg(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v163", now=TS)
    report = hyd_llg_shaped_report(
        stele, consumer_scope="project:v163", now=TS
    )
    assert report["suite"] == "hyd_llg_shaped"
    assert report["ok"] is True

    nodomain = stele.hyd_nodomain(no_domain_labels=False)
    assert nodomain["apply"] is False

    modular = stele.llg_modular(modular_merge=False)
    assert modular["apply"] is False
