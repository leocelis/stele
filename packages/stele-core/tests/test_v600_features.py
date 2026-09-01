"""v6.0: AWM workflows + RRM reflective retrieval experience."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, awm_rrm_shaped_report

TS = "2026-08-23T06:00:00Z"


def test_awm_rrm(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v60", now=TS)
    report = awm_rrm_shaped_report(
        stele, consumer_scope="project:v60", now=TS
    )
    assert report["suite"] == "awm_rrm_shaped"
    assert report["ok"] is True

    wf = stele.induce_workflow(
        task="pay invoice", steps=["open bill", "confirm", "pay"], success=True
    )
    assert wf["induced"] is True
    trig = stele.anomaly_trigger(hit_count=0, current_query="x")
    assert trig["triggered"] is True
