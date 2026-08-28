"""v10.0: Think-on-Graph + Toolformer."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, tog_toolformer_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_tog_toolformer(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v100", now=TS)
    report = tog_toolformer_shaped_report(
        stele, consumer_scope="project:v100", now=TS
    )
    assert report["suite"] == "tog_toolformer_shaped"
    assert report["ok"] is True

    prune = stele.tog_beam_prune(paths=4, keep=1)
    assert prune["apply"] is False

    exe = stele.tf_execute_proxy(api="QA")
    assert exe["apply"] is False
