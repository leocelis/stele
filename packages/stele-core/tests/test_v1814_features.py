"""v18.14: C3A + BOFT."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, c3a_bof_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_c3a_bof(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v1814", now=TS)
    report = c3a_bof_shaped_report(
        stele, consumer_scope="project:v1814", now=TS
    )
    assert report["suite"] == "c3a_bof_shaped"
    assert report["ok"] is True

    rank = stele.c3a_rank(high_rank=False)
    assert rank["apply"] is False

    full = stele.bof_full(full_rank=False)
    assert full["apply"] is False
