"""v14.9: OFT/BOFT + MiSS."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, oft_mss_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_oft_mss(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v149", now=TS)
    report = oft_mss_shaped_report(
        stele, consumer_scope="project:v149", now=TS
    )
    assert report["suite"] == "oft_mss_shaped"
    assert report["ok"] is True

    energy = stele.oft_energy(hypersphere_preserved=False)
    assert energy["apply"] is False

    pareto = stele.mss_pareto(better_tradeoff=False)
    assert pareto["apply"] is False
