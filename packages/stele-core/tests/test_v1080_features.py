"""v10.8: STaR + Cumulative Reasoning."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, star_cr_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_star_cr(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v108", now=TS)
    report = star_cr_shaped_report(
        stele, consumer_scope="project:v108", now=TS
    )
    assert report["suite"] == "star_cr_shaped"
    assert report["ok"] is True

    ft = stele.star_finetune_proxy(examples=0)
    assert ft["apply"] is False

    ver = stele.cr_verify(proposal_id="p1", valid=False)
    assert ver["apply"] is False
