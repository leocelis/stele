"""v15.0: DropLoRA + GaLore."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, drl_gal_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_drl_gal(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v150", now=TS)
    report = drl_gal_shaped_report(
        stele, consumer_scope="project:v150", now=TS
    )
    assert report["suite"] == "drl_gal_shaped"
    assert report["ok"] is True

    infer = stele.drl_infer(no_extra_cost=False)
    assert infer["apply"] is False

    full = stele.gal_full(updates_all_weights=False)
    assert full["apply"] is False
