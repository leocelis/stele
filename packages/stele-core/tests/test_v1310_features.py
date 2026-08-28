"""v13.1: TEMPERA + RLPrompt."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, tmpa_rlp_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_tmpa_rlp(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v131", now=TS)
    report = tmpa_rlp_shaped_report(
        stele, consumer_scope="project:v131", now=TS
    )
    assert report["suite"] == "tmpa_rlp_shaped"
    assert report["ok"] is True

    eff = stele.tmpa_efficiency(sample_efficient=False)
    assert eff["apply"] is False

    discrete = stele.rlp_discrete(discrete=False)
    assert discrete["apply"] is False
