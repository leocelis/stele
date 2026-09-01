"""v15.2: LoRA-Pro + Kron-LoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, lpr_krl_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_lpr_krl(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v152", now=TS)
    report = lpr_krl_shaped_report(
        stele, consumer_scope="project:v152", now=TS
    )
    assert report["suite"] == "lpr_krl_shaped"
    assert report["ok"] is True

    bridge = stele.lpr_bridge(closer_to_fft=False)
    assert bridge["apply"] is False

    compress = stele.krl_compress(more_compression=False)
    assert compress["apply"] is False
