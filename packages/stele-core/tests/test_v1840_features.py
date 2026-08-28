"""v18.4: HiRA + concurrent PLoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, hir_cnl_shaped_report

TS = "2026-08-21T12:00:00Z"


def test_hir_cnl(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v184", now=TS)
    report = hir_cnl_shaped_report(
        stele, consumer_scope="project:v184", now=TS
    )
    assert report["suite"] == "hir_cnl_shaped"
    assert report["ok"] is True

    merge = stele.hir_merge(zero_infer=False)
    assert merge["apply"] is False

    hw = stele.cnl_hw(better_util=False)
    assert hw["apply"] is False
