"""v14.7: LoHa + FourierFT."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, lha_fft_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_lha_fft(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v147", now=TS)
    report = lha_fft_shaped_report(
        stele, consumer_scope="project:v147", now=TS
    )
    assert report["suite"] == "lha_fft_shaped"
    assert report["ok"] is True

    express = stele.lha_express(more_expressivity=False)
    assert express["apply"] is False

    sparse = stele.fft_sparse(spectral_sparse=False)
    assert sparse["apply"] is False
