"""v9.5: RQ-RAG + IRCoT."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, rqrag_ircot_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_rqrag_ircot(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v95", now=TS)
    report = rqrag_ircot_shaped_report(
        stele, consumer_scope="project:v95", now=TS
    )
    assert report["suite"] == "rqrag_ircot_shaped"
    assert report["ok"] is True

    mode = stele.rqrag_refine_mode(mode="rewrite")
    assert mode["mode"] == "rewrite"

    ready = stele.ircot_answer_ready(enough=False)
    assert ready["apply"] is False
