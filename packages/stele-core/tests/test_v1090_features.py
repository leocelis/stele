"""v10.9: Plan-and-Solve + Progressive-Hint Prompting."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, ps_php_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_ps_php(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v109", now=TS)
    report = ps_php_shaped_report(
        stele, consumer_scope="project:v109", now=TS
    )
    assert report["suite"] == "ps_php_shaped"
    assert report["ok"] is True

    guard = stele.ps_calc_guard(careful=False)
    assert guard["apply"] is False

    stop = stele.php_stable_stop(same_twice=False)
    assert stop["apply"] is False
