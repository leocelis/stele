"""v17.7: MixLoRA + SuperLoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, mxl_spr_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_mxl_spr(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v177", now=TS)
    report = mxl_spr_shaped_report(
        stele, consumer_scope="project:v177", now=TS
    )
    assert report["suite"] == "mxl_spr_shaped"
    assert report["ok"] is True

    balance = stele.mxl_balance(load_balance=False)
    assert balance["apply"] is False

    unify = stele.spr_unify(unifies_loha_lokr=False)
    assert unify["apply"] is False
