"""v7.7: HyperSkill + DCPM."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, hyperskill_dcpm_shaped_report

TS = "2026-08-23T23:00:00Z"


def test_hyperskill_dcpm(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v77", now=TS)
    report = hyperskill_dcpm_shaped_report(
        stele, consumer_scope="project:v77", now=TS
    )
    assert report["suite"] == "hyperskill_dcpm_shaped"
    assert report["ok"] is True

    merge = stele.hyperskill_maintain_plan(
        utility=0.9, prune_below=0.2, redundant=True
    )
    assert merge["merge"] is True

    no_induce = stele.dcpm_night_induce(
        fact_cluster_size=1, min_cluster=3
    )
    assert no_induce["induce"] is False
