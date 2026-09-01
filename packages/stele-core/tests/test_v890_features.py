"""v8.9: RAPTOR + LightRAG."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, raptor_lightrag_shaped_report

TS = "2026-08-24T11:00:00Z"


def test_raptor_lightrag(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v89", now=TS)
    report = raptor_lightrag_shaped_report(
        stele, consumer_scope="project:v89", now=TS
    )
    assert report["suite"] == "raptor_lightrag_shaped"
    assert report["ok"] is True

    low = stele.lightrag_dual_retrieve(query="prefs", level="low")
    assert low["level"] == "low"

    empty = stele.raptor_collapsed_retrieve(candidates=0, top_k=3)
    assert empty["selected"] == 0
