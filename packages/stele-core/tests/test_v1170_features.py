"""v11.7: Active-Prompt + Analogical Prompting."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, ap_ana_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_ap_ana(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v117", now=TS)
    report = ap_ana_shaped_report(
        stele, consumer_scope="project:v117", now=TS
    )
    assert report["suite"] == "ap_ana_shaped"
    assert report["ok"] is True

    nolab = stele.ana_no_label(needs_labels=True)
    assert nolab["apply"] is False

    loop = stele.ap_loop_plan(phase="sample")
    assert loop["apply"] is False
