"""v13.5: ATTEMPT + Multitask Prompt Tuning."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, atm_mptp_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_atm_mptp(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v135", now=TS)
    report = atm_mptp_shaped_report(
        stele, consumer_scope="project:v135", now=TS
    )
    assert report["suite"] == "atm_mptp_shaped"
    assert report["ok"] is True

    mod = stele.atm_modular(modular=False)
    assert mod["apply"] is False

    eff = stele.mptp_efficient(param_efficient=False)
    assert eff["apply"] is False
