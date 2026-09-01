"""v8.2: Memanto + Zep."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, memanto_zep_shaped_report

TS = "2026-08-24T04:00:00Z"


def test_memanto_zep(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v82", now=TS)
    report = memanto_zep_shaped_report(
        stele, consumer_scope="project:v82", now=TS
    )
    assert report["suite"] == "memanto_zep_shaped"
    assert report["ok"] is True

    slow = stele.memanto_latency_gate(latency_ms=120.0, soft_cap_ms=90.0)
    assert slow["under_cap"] is False

    no_cross = stele.zep_cross_session(sessions=1, min_sessions=2)
    assert no_cross["synthesize"] is False
