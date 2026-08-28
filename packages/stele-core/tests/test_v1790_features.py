"""v17.9: Uni-LoRA + BoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, ulo_bor_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_ulo_bor(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v179", now=TS)
    report = ulo_bor_shaped_report(
        stele, consumer_scope="project:v179", now=TS
    )
    assert report["suite"] == "ulo_bor_shaped"
    assert report["ok"] is True

    one = stele.ulo_one(one_vector=False)
    assert one["apply"] is False

    sym = stele.bor_sym(symmetric=False)
    assert sym["apply"] is False
