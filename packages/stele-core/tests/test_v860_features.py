"""v8.6: MemoryBank + RF-Mem."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, memorybank_rfmem_shaped_report

TS = "2026-08-24T08:00:00Z"


def test_memorybank_rfmem(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v86", now=TS)
    report = memorybank_rfmem_shaped_report(
        stele, consumer_scope="project:v86", now=TS
    )
    assert report["suite"] == "memorybank_rfmem_shaped"
    assert report["ok"] is True

    fresh = stele.mbank_forget_curve(days_elapsed=0.1, strength=1.0)
    assert fresh["fade"] is False

    recol = stele.rfmem_path_route(mean_score=0.2, entropy=2.0)
    assert recol["path"] == "recollection"
