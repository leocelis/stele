"""v5.9: G-Memory hierarchy + MemMA probe/repair cycle."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, gmemory_memma_shaped_report

TS = "2026-08-23T05:00:00Z"


def test_gmemory_memma(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v59", now=TS)
    report = gmemory_memma_shaped_report(
        stele, consumer_scope="project:v59", now=TS
    )
    assert report["suite"] == "gmemory_memma_shaped"
    assert report["ok"] is True

    bi = stele.bidirectional_retrieve("clean", top_k=2)
    assert bi["ok"] is True
