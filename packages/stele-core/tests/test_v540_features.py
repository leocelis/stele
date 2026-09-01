"""v5.4: PAMU preference update + BEAM/HaluMem eval proxies."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, pamu_beam_shaped_report

TS = "2026-08-23T00:30:00Z"


def test_pamu_beam(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v54", now=TS)
    report = pamu_beam_shaped_report(
        stele, consumer_scope="project:v54", now=TS
    )
    assert report["suite"] == "pamu_beam_shaped"
    assert report["ok"] is True

    inv = stele.beam_category_inventory()
    assert inv["count"] == 10
