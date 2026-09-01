"""v18.8: LoRTA + C-LoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, lrt_clo_shaped_report

TS = "2026-08-22T12:00:00Z"


def test_lrt_clo(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v188", now=TS)
    report = lrt_clo_shaped_report(
        stele, consumer_scope="project:v188", now=TS
    )
    assert report["suite"] == "lrt_clo_shaped"
    assert report["ok"] is True

    compact = stele.lrt_compact(fewer_params=False)
    assert compact["apply"] is False

    forget = stele.clo_forget(less_forget=False)
    assert forget["apply"] is False
