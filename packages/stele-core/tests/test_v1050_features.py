"""v10.5: Skeleton-of-Thought + Buffer of Thoughts."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, sot_bot_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_sot_bot(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v105", now=TS)
    report = sot_bot_shaped_report(
        stele, consumer_scope="project:v105", now=TS
    )
    assert report["suite"] == "sot_bot_shaped"
    assert report["ok"] is True

    expand = stele.sot_parallel_expand(points=2)
    assert expand["apply"] is False

    upd = stele.bot_buffer_update(templates=1)
    assert upd["apply"] is False
