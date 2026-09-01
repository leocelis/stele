"""v5.3: MemEvolve architecture meta-evolution + MindMemOS/MemGuard."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, memevolve_mindmemos_shaped_report

TS = "2026-08-23T00:00:00Z"


def test_memevolve_mindmemos(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v53", now=TS)
    report = memevolve_mindmemos_shaped_report(
        stele, consumer_scope="project:v53", now=TS
    )
    assert report["suite"] == "memevolve_mindmemos_shaped"
    assert report["ok"] is True

    space = stele.list_design_space()
    assert "encode" in space and "manage" in space
