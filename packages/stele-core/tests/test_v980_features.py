"""v9.8: DSP + GenRead."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, dsp_genread_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_dsp_genread(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v98", now=TS)
    report = dsp_genread_shaped_report(
        stele, consumer_scope="project:v98", now=TS
    )
    assert report["suite"] == "dsp_genread_shaped"
    assert report["ok"] is True

    hop = stele.dsp_multihop_hop(hop=0)
    assert hop["hop"] == 0

    hyb = stele.genread_hybrid(generate=True, retrieve=False)
    assert hyb["hybrid"] is False
