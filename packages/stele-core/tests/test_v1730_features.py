"""v17.3: ReLoRA + ETHER."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, rlr_eth_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_rlr_eth(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v173", now=TS)
    report = rlr_eth_shaped_report(
        stele, consumer_scope="project:v173", now=TS
    )
    assert report["suite"] == "rlr_eth_shaped"
    assert report["ok"] is True

    high = stele.rlr_high(high_rank_update=False)
    assert high["apply"] is False

    plus = stele.eth_plus(ether_plus=False)
    assert plus["apply"] is False
