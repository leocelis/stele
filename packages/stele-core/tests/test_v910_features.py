"""v9.1: Self-RAG + MemoBrain."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, selfrag_memobrain_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_selfrag_memobrain(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v91", now=TS)
    report = selfrag_memobrain_shaped_report(
        stele, consumer_scope="project:v91", now=TS
    )
    assert report["suite"] == "selfrag_memobrain_shaped"
    assert report["ok"] is True

    need = stele.selfrag_need_retrieve(confidence=0.9, threshold=0.5)
    assert need["retrieve"] is False

    flush = stele.memobrain_flush_budget(used=10, budget=100)
    assert flush["flush"] is False
    assert flush["apply"] is False
