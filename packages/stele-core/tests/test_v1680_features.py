"""v16.8: LoRA-TSD + S-LoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, lts_slr_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_lts_slr(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v168", now=TS)
    report = lts_slr_shaped_report(
        stele, consumer_scope="project:v168", now=TS
    )
    assert report["suite"] == "lts_slr_shaped"
    assert report["ok"] is True

    combo = stele.lts_combo(uses_both=False)
    assert combo["apply"] is False

    scale = stele.slr_scale(thousands=False)
    assert scale["apply"] is False
