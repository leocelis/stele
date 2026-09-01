"""v8.7: AgeMem + MemGAS."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, agemem_memgas_shaped_report

TS = "2026-08-24T09:00:00Z"


def test_agemem_memgas(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v87", now=TS)
    report = agemem_memgas_shaped_report(
        stele, consumer_scope="project:v87", now=TS
    )
    assert report["suite"] == "agemem_memgas_shaped"
    assert report["ok"] is True

    full = stele.agemem_stm_manage(capacity=4, used=4)
    assert full["full"] is True

    coarse = stele.memgas_select_granularity(
        preferred="turn", entropy=3.0
    )
    assert coarse["chosen"] == "summary"
