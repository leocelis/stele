"""v16.7: LoRA-Mini + QDyLoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, lmi_qdy_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_lmi_qdy(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v167", now=TS)
    report = lmi_qdy_shaped_report(
        stele, consumer_scope="project:v167", now=TS
    )
    assert report["suite"] == "lmi_qdy_shaped"
    assert report["ok"] is True

    tiny = stele.lmi_tiny(extreme_compress=False)
    assert tiny["apply"] is False

    pick = stele.qdy_pick(pick_rank_at_infer=False)
    assert pick["apply"] is False
