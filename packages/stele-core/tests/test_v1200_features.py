"""v12.0: Self-Refine + Metacognitive Prompting."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, sr_mcp_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_sr_mcp(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v120", now=TS)
    report = sr_mcp_shaped_report(
        stele, consumer_scope="project:v120", now=TS
    )
    assert report["suite"] == "sr_mcp_shaped"
    assert report["ok"] is True

    nt = stele.sr_no_train(no_rl=False)
    assert nt["apply"] is False

    just = stele.mcp_justify(justified=False)
    assert just["apply"] is False

    # Meta-Prompting mp_* must remain distinct
    mp = stele.mp_loop_plan(phase="break")
    assert mp["next"] == "assign"
