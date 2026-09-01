"""v18.10: LoRAFusion + TeRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, lfu_ter_shaped_report

TS = "2026-08-22T12:00:00Z"


def test_lfu_ter(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v1810", now=TS)
    report = lfu_ter_shaped_report(
        stele, consumer_scope="project:v1810", now=TS
    )
    assert report["suite"] == "lfu_ter_shaped"
    assert report["ok"] is True

    speed = stele.lfu_speed(faster_than_mlora=False)
    assert speed["apply"] is False

    high = stele.ter_highrank(high_rank_cheap=False)
    assert high["apply"] is False
