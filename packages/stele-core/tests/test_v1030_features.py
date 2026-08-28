"""v10.3: Graph of Thoughts + Program of Thoughts."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, got_pot_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_got_pot(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v103", now=TS)
    report = got_pot_shaped_report(
        stele, consumer_scope="project:v103", now=TS
    )
    assert report["suite"] == "got_pot_shaped"
    assert report["ok"] is True

    run = stele.pot_sandbox_run(program_id="p1")
    assert run["apply"] is False

    agg = stele.got_aggregate(inputs=3)
    assert agg["apply"] is False
