"""v12.7: Automatic Prompt Engineer + Promptbreeder."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, ape_pbr_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_ape_pbr(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v127", now=TS)
    report = ape_pbr_shaped_report(
        stele, consumer_scope="project:v127", now=TS
    )
    assert report["suite"] == "ape_pbr_shaped"
    assert report["ok"] is True

    human = stele.ape_human(match_human=False)
    assert human["apply"] is False

    selfref = stele.pbr_selfref(self_improve=False)
    assert selfref["apply"] is False
