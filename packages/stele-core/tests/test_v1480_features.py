"""v14.8: Houlsby + ReFT."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, had_rft_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_had_rft(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v148", now=TS)
    report = had_rft_shaped_report(
        stele, consumer_scope="project:v148", now=TS
    )
    assert report["suite"] == "had_rft_shaped"
    assert report["ok"] is True

    latency = stele.had_latency(adds_latency=False)
    assert latency["apply"] is False

    weightless = stele.rft_weightless(no_weight_update=False)
    assert weightless["apply"] is False
