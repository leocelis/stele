"""v6.8: SkillWeaver + SkillRoute."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, skillweaver_skillroute_shaped_report

TS = "2026-08-23T14:00:00Z"


def test_skillweaver_skillroute(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v68", now=TS)
    report = skillweaver_skillroute_shaped_report(
        stele, consumer_scope="project:v68", now=TS
    )
    assert report["suite"] == "skillweaver_skillroute_shaped"
    assert report["ok"] is True

    g = stele.granularity_match_check(step_count=3, expected_skills=2)
    assert g["da_match"] is False
    t = stele.transfer_skill_gate(
        donor_success_rate=0.2, recipient_baseline=0.5
    )
    assert t["transfer_worth"] is False
