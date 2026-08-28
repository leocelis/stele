"""v17.6: FlyLoRA + NOLA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, fly_nla_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_fly_nla(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v176", now=TS)
    report = fly_nla_shaped_report(
        stele, consumer_scope="project:v176", now=TS
    )
    assert report["suite"] == "fly_nla_shaped"
    assert report["ok"] is True

    implicit = stele.fly_implicit(implicit_router=False)
    assert implicit["apply"] is False

    compact = stele.nla_compact(beyond_rank1=False)
    assert compact["apply"] is False
