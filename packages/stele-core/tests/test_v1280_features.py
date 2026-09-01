"""v12.8: OPRO + EvoPrompt."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, opro_evp_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_opro_evp(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v128", now=TS)
    report = opro_evp_shaped_report(
        stele, consumer_scope="project:v128", now=TS
    )
    assert report["suite"] == "opro_evp_shaped"
    assert report["ok"] is True

    best = stele.opro_best(beat_human=False)
    assert best["apply"] is False

    ea = stele.evp_ea(connect_ea=False)
    assert ea["apply"] is False
