"""v10.2: Tree of Thoughts + Least-to-Most."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, tot_ltm_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_tot_ltm(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v102", now=TS)
    report = tot_ltm_shaped_report(
        stele, consumer_scope="project:v102", now=TS
    )
    assert report["suite"] == "tot_ltm_shaped"
    assert report["ok"] is True

    bt = stele.tot_backtrack(from_node="n1")
    assert bt["apply"] is False

    eth = stele.ltm_easy_to_hard(exemplars=3)
    assert eth["exemplars"] == 3
