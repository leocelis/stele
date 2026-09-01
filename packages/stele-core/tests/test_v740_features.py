"""v7.4: Socratic-Zero + SPIRAL."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, socratic_spiral_shaped_report

TS = "2026-08-23T20:00:00Z"


def test_socratic_spiral(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v74", now=TS)
    report = socratic_spiral_shaped_report(
        stele, consumer_scope="project:v74", now=TS
    )
    assert report["suite"] == "socratic_spiral_shaped"
    assert report["ok"] is True

    not_ready = stele.socratic_seed_bootstrap(seed_count=10, min_seeds=100)
    assert not_ready["ready"] is False
