"""v16.1: LoRAShear + alternating OPLoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, lsh_aop_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_lsh_aop(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v161", now=TS)
    report = lsh_aop_shaped_report(
        stele, consumer_scope="project:v161", now=TS
    )
    assert report["suite"] == "lsh_aop_shaped"
    assert report["ok"] is True

    foot = stele.lsh_footprint(reduced=False)
    assert foot["apply"] is False

    svd = stele.aop_svd(near_svd=False)
    assert svd["apply"] is False
