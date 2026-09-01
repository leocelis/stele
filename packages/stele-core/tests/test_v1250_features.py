"""v12.5: Self-Verification + Chain of Density."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, sve_cod_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_sve_cod(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v125", now=TS)
    report = sve_cod_shaped_report(
        stele, consumer_scope="project:v125", now=TS
    )
    assert report["suite"] == "sve_cod_shaped"
    assert report["ok"] is True

    sel = stele.sve_select(pick_best=False)
    assert sel["apply"] is False

    trade = stele.cod_tradeoff(prefer_dense=False)
    assert trade["apply"] is False
