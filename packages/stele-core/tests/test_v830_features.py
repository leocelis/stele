"""v8.3: MemGPT + RippleMem."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, memgpt_ripple_shaped_report

TS = "2026-08-24T05:00:00Z"


def test_memgpt_ripple(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v83", now=TS)
    report = memgpt_ripple_shaped_report(
        stele, consumer_scope="project:v83", now=TS
    )
    assert report["suite"] == "memgpt_ripple_shaped"
    assert report["ok"] is True

    flush = stele.memgpt_main_capacity(
        used_tokens=1000, max_tokens=1000, warn_ratio=0.7
    )
    assert flush["flush"] is True

    incomplete = stele.ripple_recollect_gate(seed_hits=2, associated=0)
    assert incomplete["complete"] is False
