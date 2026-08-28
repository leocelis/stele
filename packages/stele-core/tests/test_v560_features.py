"""v5.6: MemoryOS STM/MTM/LPM heat + NEMORI prediction-error distill."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, memoryos_nemori_shaped_report

TS = "2026-08-23T02:00:00Z"


def test_memoryos_nemori(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v56", now=TS)
    report = memoryos_nemori_shaped_report(
        stele, consumer_scope="project:v56", now=TS
    )
    assert report["suite"] == "memoryos_nemori_shaped"
    assert report["ok"] is True

    heat = stele.heat_score(n_visit=2, l_interaction=2, delta_t_seconds=0.0)
    assert heat["heat"] > 0
    gate = stele.deserves_memory_gate(
        actual="brand new quantum purple widget fact",
        anticipated="(no prior)",
    )
    assert gate["admit"] is True
