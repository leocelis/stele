"""v18.11: TensLoRA + AdaZeta."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, tnl_azt_shaped_report

TS = "2026-08-22T12:00:00Z"


def test_tnl_azt(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v1811", now=TS)
    report = tnl_azt_shaped_report(
        stele, consumer_scope="project:v1811", now=TS
    )
    assert report["suite"] == "tnl_azt_shaped"
    assert report["ok"] is True

    budget = stele.tnl_budget(mode_specific=False)
    assert budget["apply"] is False

    mem = stele.azt_mem(zo_memory=False)
    assert mem["apply"] is False
