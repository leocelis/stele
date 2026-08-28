"""v8.4: FluxMem + QUMem."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, fluxmem_qumem_shaped_report

TS = "2026-08-24T06:00:00Z"


def test_fluxmem_qumem(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v84", now=TS)
    report = fluxmem_qumem_shaped_report(
        stele, consumer_scope="project:v84", now=TS
    )
    assert report["suite"] == "fluxmem_qumem_shaped"
    assert report["ok"] is True

    immature = stele.flux_maturity_gate(
        generalizability=0.2, min_score=0.5
    )
    assert immature["mature"] is False

    stale = stele.qumem_temporal_valid(
        event_ts="2025-01-01T00:00:00Z",
        query_ts="2026-08-01T00:00:00Z",
        stale=True,
    )
    assert stale["valid"] is False
