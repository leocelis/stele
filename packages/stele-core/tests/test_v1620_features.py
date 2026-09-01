"""v16.2: LoRA-Init + LoRA-Null."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, lin_lnu_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_lin_lnu(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v162", now=TS)
    report = lin_lnu_shaped_report(
        stele, consumer_scope="project:v162", now=TS
    )
    assert report["suite"] == "lin_lnu_shaped"
    assert report["ok"] is True

    fast = stele.lin_fast(faster_convergence=False)
    assert fast["apply"] is False

    forget = stele.lnu_forget(preserves_knowledge=False)
    assert forget["apply"] is False
