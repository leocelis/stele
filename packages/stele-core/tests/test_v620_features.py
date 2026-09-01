"""v6.2: ExpeL + RMM dialogue reflection."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, expel_rmm_shaped_report

TS = "2026-08-23T08:00:00Z"


def test_expel_rmm(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v62", now=TS)
    report = expel_rmm_shaped_report(
        stele, consumer_scope="project:v62", now=TS
    )
    assert report["suite"] == "expel_rmm_shaped"
    assert report["ok"] is True

    op = stele.insight_op([], op="ADD", text="check env assumptions")
    assert op["ok"] is True
    mem = stele.prospective_reflect(
        topic="prefs", segment="likes concise answers", granularity="utterance"
    )
    assert mem["ok"] is True
