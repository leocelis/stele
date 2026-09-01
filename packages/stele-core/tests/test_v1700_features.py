"""v17.0: Punica + mLoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, pun_mla_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_pun_mla(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v170", now=TS)
    report = pun_mla_shaped_report(
        stele, consumer_scope="project:v170", now=TS
    )
    assert report["suite"] == "pun_mla_shaped"
    assert report["ok"] is True

    multi = stele.pun_multi(multi_tenant=False)
    assert multi["apply"] is False

    eff = stele.mla_eff(lower_completion_time=False)
    assert eff["apply"] is False
