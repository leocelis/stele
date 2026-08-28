"""v9.6: REPLUG + Iter-RetGen."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, replug_iterretgen_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_replug_iterretgen(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v96", now=TS)
    report = replug_iterretgen_shaped_report(
        stele, consumer_scope="project:v96", now=TS
    )
    assert report["suite"] == "replug_iterretgen_shaped"
    assert report["ok"] is True

    stop = stele.iterretgen_iterate(round_n=3, max_rounds=3)
    assert stop["continue"] is False

    sup = stele.replug_supervise_retriever(lm_gain=0.5)
    assert sup["apply"] is False
