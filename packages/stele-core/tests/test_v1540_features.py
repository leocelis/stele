"""v15.4: LoftQ + LoRA-Dash."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, lfq_lds_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_lfq_lds(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v154", now=TS)
    report = lfq_lds_shaped_report(
        stele, consumer_scope="project:v154", now=TS
    )
    assert report["suite"] == "lfq_lds_shaped"
    assert report["ok"] is True

    gap = stele.lfq_gap(closes_qlora_gap=False)
    assert gap["apply"] is False

    impact = stele.lds_impact(maximizes_tsd=False)
    assert impact["apply"] is False
