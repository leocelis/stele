"""v14.3: LoRA-FA + DyLoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, lfa_dyl_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_lfa_dyl(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v143", now=TS)
    report = lfa_dyl_shaped_report(
        stele, consumer_scope="project:v143", now=TS
    )
    assert report["suite"] == "lfa_dyl_shaped"
    assert report["ok"] is True

    mem = stele.lfa_memory(activation_saved=False)
    assert mem["apply"] is False

    searchfree = stele.dyl_searchfree(search_free=False)
    assert searchfree["apply"] is False
