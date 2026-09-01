"""v8.5: VikingMem + RecMem."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, vikingmem_recmem_shaped_report

TS = "2026-08-24T07:00:00Z"


def test_vikingmem_recmem(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v85", now=TS)
    report = vikingmem_recmem_shaped_report(
        stele, consumer_scope="project:v85", now=TS
    )
    assert report["suite"] == "vikingmem_recmem_shaped"
    assert report["ok"] is True

    low = stele.viking_extract_event(content="noise", high_value=False)
    assert low["kept"] is False

    no_trig = stele.recmem_recurrence_gate(similar_count=2, threshold=5)
    assert no_trig["trigger"] is False
