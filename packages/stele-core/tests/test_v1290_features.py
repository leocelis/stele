"""v12.9: ProTeGi + PromptAgent."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, ptg_pag_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_ptg_pag(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v129", now=TS)
    report = ptg_pag_shaped_report(
        stele, consumer_scope="project:v129", now=TS
    )
    assert report["suite"] == "ptg_pag_shaped"
    assert report["ok"] is True

    jb = stele.ptg_jailbreak(detect=False)
    assert jb["apply"] is False

    expert = stele.pag_expert(expert_level=False)
    assert expert["apply"] is False
