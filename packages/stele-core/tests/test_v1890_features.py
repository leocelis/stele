"""v18.9: ALoRA + LN Tuning."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, alo_lnt_shaped_report

TS = "2026-08-22T12:00:00Z"


def test_alo_lnt(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v189", now=TS)
    report = alo_lnt_shaped_report(
        stele, consumer_scope="project:v189", now=TS
    )
    assert report["suite"] == "alo_lnt_shaped"
    assert report["ok"] is True

    realloc = stele.alo_realloc(dynamic=False)
    assert realloc["apply"] is False

    cheap = stele.lnt_cheap(cheaper_than_lora=False)
    assert cheap["apply"] is False
