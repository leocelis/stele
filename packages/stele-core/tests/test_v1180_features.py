"""v11.8: Complexity-Based + Step-Back Prompting."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, cbp_sb_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_cbp_sb(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v118", now=TS)
    report = cbp_sb_shaped_report(
        stele, consumer_scope="project:v118", now=TS
    )
    assert report["suite"] == "cbp_sb_shaped"
    assert report["ok"] is True

    vote = stele.cbp_vote_complex(prefer_complex=False)
    assert vote["apply"] is False

    trap = stele.sb_detail_trap(escaped=False)
    assert trap["apply"] is False
