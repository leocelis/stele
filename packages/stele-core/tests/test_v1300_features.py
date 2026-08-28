"""v13.0: MAPO + GrIPS."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, mapo_grips_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_mapo_grips(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v130", now=TS)
    report = mapo_grips_shaped_report(
        stele, consumer_scope="project:v130", now=TS
    )
    assert report["suite"] == "mapo_grips_shaped"
    assert report["ok"] is True

    faster = stele.mapo_faster(beat_protegi=False)
    assert faster["apply"] is False

    api = stele.grips_api(api_tunable=False)
    assert api["apply"] is False
