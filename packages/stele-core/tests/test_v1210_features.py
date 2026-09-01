"""v12.1: Thread of Thought + Thought Propagation."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, thot_tprop_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_thot_tprop(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v121", now=TS)
    report = thot_tprop_shaped_report(
        stele, consumer_scope="project:v121", now=TS
    )
    assert report["suite"] == "thot_tprop_shaped"
    assert report["ok"] is True

    plug = stele.thot_plug(plug_and_play=False)
    assert plug["apply"] is False

    compat = stele.tprop_compat(plug_and_play=False)
    assert compat["apply"] is False
