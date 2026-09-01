"""v15.8: LoRA-drop + VB-LoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, ldr_vbl_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_ldr_vbl(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v158", now=TS)
    report = ldr_vbl_shaped_report(
        stele, consumer_scope="project:v158", now=TS
    )
    assert report["suite"] == "ldr_vbl_shaped"
    assert report["ok"] is True

    prune = stele.ldr_prune(half_params=False)
    assert prune["apply"] is False

    extreme = stele.vbl_extreme(extreme_compression=False)
    assert extreme["apply"] is False
