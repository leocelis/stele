"""v12.6: Hint-before-Solving + EmotionPrompt."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, hsp_emo_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_hsp_emo(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v126", now=TS)
    report = hsp_emo_shaped_report(
        stele, consumer_scope="project:v126", now=TS
    )
    assert report["suite"] == "hsp_emo_shaped"
    assert report["ok"] is True

    qual = stele.hsp_quality(high_quality=False)
    assert qual["apply"] is False

    psych = stele.emo_psych(psychology=False)
    assert psych["apply"] is False
