"""v9.4: GraphReader + G-Retriever."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, graphreader_gretriever_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_graphreader_gretriever(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v94", now=TS)
    report = graphreader_gretriever_shaped_report(
        stele, consumer_scope="project:v94", now=TS
    )
    assert report["suite"] == "graphreader_gretriever_shaped"
    assert report["ok"] is True

    pcst = stele.gretriever_pcst_select(nodes=2, budget=10)
    assert pcst["selected"] == 2

    reflect = stele.graphreader_reflect_plan(enough=False)
    assert reflect["apply"] is False
