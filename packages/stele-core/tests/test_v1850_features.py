"""v18.5: LongLoRA + LISA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, llr_lis_shaped_report

TS = "2026-08-21T12:00:00Z"


def test_llr_lis(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v185", now=TS)
    report = llr_lis_shaped_report(
        stele, consumer_scope="project:v185", now=TS
    )
    assert report["suite"] == "llr_lis_shaped"
    assert report["ok"] is True

    sparse = stele.llr_sparse(sparse_train=False)
    assert sparse["apply"] is False

    mem = stele.lis_memory(less_opt=False)
    assert mem["apply"] is False
