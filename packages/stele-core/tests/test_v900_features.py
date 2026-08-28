"""v9.0: MemoRAG + PageIndex."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, memorag_pageindex_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_memorag_pageindex(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v90", now=TS)
    report = memorag_pageindex_shaped_report(
        stele, consumer_scope="project:v90", now=TS
    )
    assert report["suite"] == "memorag_pageindex_shaped"
    assert report["ok"] is True

    gen = stele.memorag_dual_system(role="generator")
    assert gen["role"] == "generator"

    prune = stele.pageindex_select_section(
        section_id="sec1", relevant=False
    )
    assert prune["kept"] is False
