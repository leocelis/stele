"""v18.2: BoHA + SMoA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, bha_smo_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_bha_smo(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v182", now=TS)
    report = bha_smo_shaped_report(
        stele, consumer_scope="project:v182", now=TS
    )
    assert report["suite"] == "bha_smo_shaped"
    assert report["ok"] is True

    local = stele.bha_local(localized=False)
    assert local["apply"] is False

    rank = stele.smo_rank(high_rank=False)
    assert rank["apply"] is False
