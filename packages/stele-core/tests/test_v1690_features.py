"""v16.9: Compress-then-Serve + FLoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, cts_flo_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_cts_flo(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v169", now=TS)
    report = cts_flo_shaped_report(
        stele, consumer_scope="project:v169", now=TS
    )
    assert report["suite"] == "cts_flo_shaped"
    assert report["ok"] is True

    cluster = stele.cts_cluster(cluster_for_large=False)
    assert cluster["apply"] is False

    hetero = stele.flo_hetero(supports_hetero=False)
    assert hetero["apply"] is False
