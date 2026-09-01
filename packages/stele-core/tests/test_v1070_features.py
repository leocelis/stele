"""v10.7: Quiet-STaR + Decomposed Prompting."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, qs_dep_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_qs_dep(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v107", now=TS)
    report = qs_dep_shaped_report(
        stele, consumer_scope="project:v107", now=TS
    )
    assert report["suite"] == "qs_dep_shaped"
    assert report["ok"] is True

    zs = stele.qs_zero_shot_flag(improved=False)
    assert zs["apply"] is False

    swap = stele.dep_swap_symbolic(module="calc")
    assert swap["apply"] is False
