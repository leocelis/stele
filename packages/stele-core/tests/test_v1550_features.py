"""v15.5: Delta-LoRA + LoRA-One."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, dlo_lon_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_dlo_lon(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v155", now=TS)
    report = dlo_lon_shaped_report(
        stele, consumer_scope="project:v155", now=TS
    )
    assert report["suite"] == "dlo_lon_shaped"
    assert report["ok"] is True

    high = stele.dlo_highrank(high_rank_capacity=False)
    assert high["apply"] is False

    imm = stele.lon_immediate(immediate_align=False)
    assert imm["apply"] is False
