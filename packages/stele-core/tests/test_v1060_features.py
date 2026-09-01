"""v10.6: Self-Discover + Meta-Prompting."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, sd_mp_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_sd_mp(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v106", now=TS)
    report = sd_mp_shaped_report(
        stele, consumer_scope="project:v106", now=TS
    )
    assert report["suite"] == "sd_mp_shaped"
    assert report["ok"] is True

    apply = stele.sd_apply_instance(structure_id="s1")
    assert apply["apply"] is False

    verify = stele.mp_verify(claim="ok")
    assert verify["apply"] is False
