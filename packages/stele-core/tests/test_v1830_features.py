"""v18.3: GLoRA + PeriodicLoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, glo_plr_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_glo_plr(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v183", now=TS)
    report = glo_plr_shaped_report(
        stele, consumer_scope="project:v183", now=TS
    )
    assert report["suite"] == "glo_plr_shaped"
    assert report["ok"] is True

    zero = stele.glo_zero(zero_infer=False)
    assert zero["apply"] is False

    rank = stele.plr_rank(accum_rank=False)
    assert rank["apply"] is False
