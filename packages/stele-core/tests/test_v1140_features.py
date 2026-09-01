"""v11.4: HuggingGPT + Multiagent Debate."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, hgpt_mad_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_hgpt_mad(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v114", now=TS)
    report = hgpt_mad_shaped_report(
        stele, consumer_scope="project:v114", now=TS
    )
    assert report["suite"] == "hgpt_mad_shaped"
    assert report["ok"] is True

    exe = stele.hgpt_execute(selection_id="abc")
    assert exe["apply"] is False

    conv = stele.mad_converge(common=False)
    assert conv["apply"] is False
