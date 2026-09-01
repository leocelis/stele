"""v7.6: HiMem + H-MEM levels."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, himem_hmeml_shaped_report

TS = "2026-08-23T22:00:00Z"


def test_himem_hmeml(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v76", now=TS)
    report = himem_hmeml_shaped_report(
        stele, consumer_scope="project:v76", now=TS
    )
    assert report["suite"] == "himem_hmeml_shaped"
    assert report["ok"] is True

    best = stele.himem_retrieve_strategy(
        mode="best_effort", note_hit=False
    )
    assert best["use_episodes"] is True

    miss = stele.hmeml_descend(current_level="content", hit=False)
    assert miss["action"] == "exhausted"
