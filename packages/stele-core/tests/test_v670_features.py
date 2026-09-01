"""v6.7: EvolveR + AgentEvolver."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, evolver_agentevolver_shaped_report

TS = "2026-08-23T13:00:00Z"


def test_evolver_agentevolver(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v67", now=TS)
    report = evolver_agentevolver_shaped_report(
        stele, consumer_scope="project:v67", now=TS
    )
    assert report["suite"] == "evolver_agentevolver_shaped"
    assert report["ok"] is True

    f = stele.distill_principle(
        kind="failure", description="do not answer before searching both"
    )
    assert f["kind"] == "failure"
    m = stele.mixed_rollout_split(total_rollouts=5, eta=0.0)
    assert m["guided"] == 0 and m["vanilla"] == 5
