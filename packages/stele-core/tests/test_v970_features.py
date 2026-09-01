"""v9.7: PlanRAG + Rewrite-Retrieve-Read."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, planrag_rrr_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_planrag_rrr(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v97", now=TS)
    report = planrag_rrr_shaped_report(
        stele, consumer_scope="project:v97", now=TS
    )
    assert report["suite"] == "planrag_rrr_shaped"
    assert report["ok"] is True

    decide = stele.planrag_decide(ready=False)
    assert decide["decided"] is False

    train = stele.rrr_train_rewriter_plan(improve=False)
    assert train["apply"] is False
