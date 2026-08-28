"""v8.8: MemWalker + MemGraphRAG."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, memwalker_memgraphrag_shaped_report

TS = "2026-08-24T10:00:00Z"


def test_memwalker_memgraphrag(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v88", now=TS)
    report = memwalker_memgraphrag_shaped_report(
        stele, consumer_scope="project:v88", now=TS
    )
    assert report["suite"] == "memwalker_memgraphrag_shaped"
    assert report["ok"] is True

    deep = stele.memwalker_path_gate(depth=10, max_depth=3)
    assert deep["within"] is False

    clean = stele.mgr_detect_conflict(facts=5, anomalies=0)
    assert clean["conflict"] is False
