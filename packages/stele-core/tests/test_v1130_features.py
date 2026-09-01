"""v11.3: CRITIC + Deductive Verification."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, critic_dv_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_critic_dv(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v113", now=TS)
    report = critic_dv_shaped_report(
        stele, consumer_scope="project:v113", now=TS
    )
    assert report["suite"] == "critic_dv_shaped"
    assert report["ok"] is True

    stop = stele.critic_stop(satisfied=False)
    assert stop["apply"] is False

    uni = stele.dv_unanimity(all_pass=False)
    assert uni["apply"] is False
