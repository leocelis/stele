"""v13.2: AutoPrompt + Prefix-Tuning."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, aup_pfx_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_aup_pfx(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v132", now=TS)
    report = aup_pfx_shaped_report(
        stele, consumer_scope="project:v132", now=TS
    )
    assert report["suite"] == "aup_pfx_shaped"
    assert report["ok"] is True

    probe = stele.aup_probe(parameter_free=False)
    assert probe["apply"] is False

    freeze = stele.pfx_freeze(freeze_lm=False)
    assert freeze["apply"] is False
