"""v14.0: VeRA + AdapterDrop."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, vra_adp_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_vra_adp(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v140", now=TS)
    report = vra_adp_shaped_report(
        stele, consumer_scope="project:v140", now=TS
    )
    assert report["suite"] == "vra_adp_shaped"
    assert report["ok"] is True

    tiny = stele.vra_tiny(vector_only=False)
    assert tiny["apply"] is False

    efficient = stele.adp_efficient(multi_task=False)
    assert efficient["apply"] is False
