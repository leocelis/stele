"""v18.7: HRA + Hybrid PEFT."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, hra_hyb_shaped_report

TS = "2026-08-22T12:00:00Z"


def test_hra_hyb(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v187", now=TS)
    report = hra_hyb_shaped_report(
        stele, consumer_scope="project:v187", now=TS
    )
    assert report["suite"] == "hra_hyb_shaped"
    assert report["ok"] is True

    ortho = stele.hra_ortho(ortho_stable=False)
    assert ortho["apply"] is False

    stable = stele.hyb_stable(more_stable=False)
    assert stable["apply"] is False
