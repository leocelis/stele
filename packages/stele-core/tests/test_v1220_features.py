"""v12.2: System 2 Attention + Contrastive CoT."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, s2a_ccot_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_s2a_ccot(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v122", now=TS)
    report = s2a_ccot_shaped_report(
        stele, consumer_scope="project:v122", now=TS
    )
    assert report["suite"] == "s2a_ccot_shaped"
    assert report["ok"] is True

    syc = stele.s2a_sycophancy(reduced=False)
    assert syc["apply"] is False

    auto = stele.ccot_auto(construct=False)
    assert auto["apply"] is False
