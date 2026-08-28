"""v9.2: CRAG + HyDE."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, crag_hyde_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_crag_hyde(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v92", now=TS)
    report = crag_hyde_shaped_report(
        stele, consumer_scope="project:v92", now=TS
    )
    assert report["suite"] == "crag_hyde_shaped"
    assert report["ok"] is True

    bad = stele.crag_evaluate_retrieval(confidence=0.1)
    assert bad["action"] == "Incorrect"

    web = stele.crag_web_fallback_plan(trigger=True)
    assert web["apply"] is False
