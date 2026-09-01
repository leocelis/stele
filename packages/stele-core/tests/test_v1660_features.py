"""v16.6: MTL-LoRA + MALoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, mtl_mal_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_mtl_mal(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v166", now=TS)
    report = mtl_mal_shaped_report(
        stele, consumer_scope="project:v166", now=TS
    )
    assert report["suite"] == "mtl_mal_shaped"
    assert report["ok"] is True

    interfere = stele.mtl_interfere(less_interference=False)
    assert interfere["apply"] is False

    eff = stele.mal_eff(fewer_params=False)
    assert eff["apply"] is False
