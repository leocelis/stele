"""v16.0: GeoLoRA + RandLoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, geo_rlo_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_geo_rlo(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v160", now=TS)
    report = geo_rlo_shaped_report(
        stele, consumer_scope="project:v160", now=TS
    )
    assert report["suite"] == "geo_rlo_shaped"
    assert report["ok"] is True

    ortho = stele.geo_ortho(exact_ortho=False)
    assert ortho["apply"] is False

    full = stele.rlo_fullrank(full_rank_update=False)
    assert full["apply"] is False
