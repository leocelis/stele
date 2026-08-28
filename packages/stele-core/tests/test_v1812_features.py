"""v18.12: FacT + LoTR."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, fct_ltr_shaped_report

TS = "2026-08-22T12:00:00Z"


def test_fct_ltr(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v1812", now=TS)
    report = fct_ltr_shaped_report(
        stele, consumer_scope="project:v1812", now=TS
    )
    assert report["suite"] == "fct_ltr_shaped"
    assert report["ok"] is True

    tiny = stele.fct_tiny(tiny_params=False)
    assert tiny["apply"] is False

    deep = stele.ltr_deep(better_for_deep=False)
    assert deep["apply"] is False
