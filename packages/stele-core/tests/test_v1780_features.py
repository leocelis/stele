"""v17.8: Tied-LoRA + QA-LoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, tld_qal_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_tld_qal(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v178", now=TS)
    report = tld_qal_shaped_report(
        stele, consumer_scope="project:v178", now=TS
    )
    assert report["suite"] == "tld_qal_shaped"
    assert report["ok"] is True

    frac = stele.tld_frac(fraction_of_lora=False)
    assert frac["apply"] is False

    merge = stele.qal_merge(merge_int4=False)
    assert merge["apply"] is False
