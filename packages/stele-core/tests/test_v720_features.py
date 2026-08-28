"""v7.2: MemGen + Metis."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, memgen_metis_shaped_report

TS = "2026-08-23T18:00:00Z"


def test_memgen_metis(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v72", now=TS)
    report = memgen_metis_shaped_report(
        stele, consumer_scope="project:v72", now=TS
    )
    assert report["suite"] == "memgen_metis_shaped"
    assert report["ok"] is True

    no_promo = stele.crystallize_plan_to_tool(
        plan_id="p1", reuse_count=1, min_reuse=3
    )
    assert no_promo["promote"] is False
