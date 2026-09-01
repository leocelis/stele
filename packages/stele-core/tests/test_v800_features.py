"""v8.0: MemEngine + SimpleMem."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, memengine_simplemem_shaped_report

TS = "2026-08-24T02:00:00Z"


def test_memengine_simplemem(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v80", now=TS)
    report = memengine_simplemem_shaped_report(
        stele, consumer_scope="project:v80", now=TS
    )
    assert report["suite"] == "memengine_simplemem_shaped"
    assert report["ok"] is True

    simple = stele.simplemem_intent_scope(complexity="simple")
    assert simple["k"] == 3

    no_syn = stele.simplemem_synthesize(related_facts=1, min_related=2)
    assert no_syn["synthesize"] is False
