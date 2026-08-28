"""v15.9: OPLoRA + GeLoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, opl_gel_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_opl_gel(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v159", now=TS)
    report = opl_gel_shaped_report(
        stele, consumer_scope="project:v159", now=TS
    )
    assert report["suite"] == "opl_gel_shaped"
    assert report["ok"] is True

    forget = stele.opl_forget(less_forgetting=False)
    assert forget["apply"] is False

    budget = stele.gel_budget(within_budget=False)
    assert budget["apply"] is False
