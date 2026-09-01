"""v7.5: SMITH + H-Mem."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, smith_hmem_shaped_report

TS = "2026-08-23T21:00:00Z"


def test_smith_hmem(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v75", now=TS)
    report = smith_hmem_shaped_report(
        stele, consumer_scope="project:v75", now=TS
    )
    assert report["suite"] == "smith_hmem_shaped"
    assert report["ok"] is True

    hard = stele.smith_curriculum_difficulty(ensemble_fail_rate=0.9)
    assert hard["band"] == "hard"
