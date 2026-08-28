"""v14.6: rsLoRA + LoKr."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, rsl_lkr_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_rsl_lkr(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v146", now=TS)
    report = rsl_lkr_shaped_report(
        stele, consumer_scope="project:v146", now=TS
    )
    assert report["suite"] == "rsl_lkr_shaped"
    assert report["ok"] is True

    stable = stele.rsl_stable(no_collapse=False)
    assert stable["apply"] is False

    preserve = stele.lkr_preserve(rank_preserved=False)
    assert preserve["apply"] is False
