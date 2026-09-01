"""v11.0: AgentCoder + PAL."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, ac_pal_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_ac_pal(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v110", now=TS)
    report = ac_pal_shaped_report(
        stele, consumer_scope="project:v110", now=TS
    )
    assert report["suite"] == "ac_pal_shaped"
    assert report["ok"] is True

    gate = stele.ac_pass_gate(all_pass=False)
    assert gate["apply"] is False

    off = stele.pal_offload_solve(program_id="abc")
    assert off["apply"] is False
