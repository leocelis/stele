"""v18.13: CaRA + LoRETTA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, cra_ltt_shaped_report

TS = "2026-08-22T12:00:00Z"


def test_cra_ltt(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v1813", now=TS)
    report = cra_ltt_shaped_report(
        stele, consumer_scope="project:v1813", now=TS
    )
    assert report["suite"] == "cra_ltt_shaped"
    assert report["ok"] is True

    heads = stele.cra_heads(head_mode=False)
    assert heads["apply"] is False

    tiny = stele.ltt_tiny(sub_mb=False)
    assert tiny["apply"] is False
