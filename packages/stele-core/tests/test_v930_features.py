"""v9.3: Adaptive-RAG + FLARE."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, adaptiverag_flare_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_adaptiverag_flare(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v93", now=TS)
    report = adaptiverag_flare_shaped_report(
        stele, consumer_scope="project:v93", now=TS
    )
    assert report["suite"] == "adaptiverag_flare_shaped"
    assert report["ok"] is True

    simple = stele.adaptiverag_classify_complexity(hops=0)
    assert simple["level"] == 0

    high = stele.flare_low_confidence(confidence=0.9, threshold=0.4)
    assert high["low"] is False
