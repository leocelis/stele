"""v6.5: PreFlect + SkillFlow."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, preflect_skillflow_shaped_report

TS = "2026-08-23T11:00:00Z"


def test_preflect_skillflow(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v65", now=TS)
    report = preflect_skillflow_shaped_report(
        stele, consumer_scope="project:v65", now=TS
    )
    assert report["suite"] == "preflect_skillflow_shaped"
    assert report["ok"] is True

    g = stele.preflect_before_execute_gate(
        critique_needs_revise=False, revised_ready=False
    )
    assert g["allowed"] is True
    c = stele.skill_curation_decide(
        mean_log_flow=-0.1,
        centered_log_share=0.0,
        high_importance_step=True,
    )
    assert c["decision"] == "create"
