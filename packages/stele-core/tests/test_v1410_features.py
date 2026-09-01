"""v14.1: PiSSA + Diff Pruning."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, psa_dpr_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_psa_dpr(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v141", now=TS)
    report = psa_dpr_shaped_report(
        stele, consumer_scope="project:v141", now=TS
    )
    assert report["suite"] == "psa_dpr_shaped"
    assert report["ok"] is True

    fast = stele.psa_fast(faster_than_lora=False)
    assert fast["apply"] is False

    sparse = stele.dpr_sparse(no_new_params=False)
    assert sparse["apply"] is False
