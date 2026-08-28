"""v5.5: REMem episodic graph + EverMemOS MemCell/MemScene."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, remem_evermemos_shaped_report

TS = "2026-08-23T01:00:00Z"


def test_remem_evermemos(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v55", now=TS)
    report = remem_evermemos_shaped_report(
        stele, consumer_scope="project:v55", now=TS
    )
    assert report["suite"] == "remem_evermemos_shaped"
    assert report["ok"] is True

    graph = stele.build_hybrid_episodic_graph()
    assert graph["gist_count"] >= 1
