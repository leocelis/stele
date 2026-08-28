"""v12.3: Tab-CoT + Everything of Thoughts."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, tabcot_xot_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_tabcot_xot(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v123", now=TS)
    report = tabcot_xot_shaped_report(
        stele, consumer_scope="project:v123", now=TS
    )
    assert report["suite"] == "tabcot_xot_shaped"
    assert report["ok"] is True

    zs = stele.tabcot_zeroshot(zero_shot=False)
    assert zs["apply"] is False

    flex = stele.xot_flexible(multi_solution=False)
    assert flex["apply"] is False
