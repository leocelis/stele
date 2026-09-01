"""v11.1: Faithful CoT + LATS."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, fcot_lats_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_fcot_lats(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v111", now=TS)
    report = fcot_lats_shaped_report(
        stele, consumer_scope="project:v111", now=TS
    )
    assert report["suite"] == "fcot_lats_shaped"
    assert report["ok"] is True

    sol = stele.fcot_solve(chain_id="abc")
    assert sol["apply"] is False

    env = stele.lats_env_feedback(useful=False)
    assert env["apply"] is False
