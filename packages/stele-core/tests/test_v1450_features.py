"""v14.5: LoRA-GA + MoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, lga_mor_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_lga_mor(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v145", now=TS)
    report = lga_mor_shaped_report(
        stele, consumer_scope="project:v145", now=TS
    )
    assert report["suite"] == "lga_mor_shaped"
    assert report["ok"] is True

    fast = stele.lga_fast(faster_convergence=False)
    assert fast["apply"] is False

    merge = stele.mor_merge(mergeable=False)
    assert merge["apply"] is False
