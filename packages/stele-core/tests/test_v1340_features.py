"""v13.4: Soft Prompt Mixtures + SPoT."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, msp_spot_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_msp_spot(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v134", now=TS)
    report = msp_spot_shaped_report(
        stele, consumer_scope="project:v134", now=TS
    )
    assert report["suite"] == "msp_spot_shaped"
    assert report["ok"] is True

    under = stele.msp_underest(prior_underestimate=False)
    assert under["apply"] is False

    vs = stele.spot_vs_tune(beat_model_tuning=False)
    assert vs["apply"] is False
