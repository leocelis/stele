"""v12.4: Chain-of-Verification + Verify-and-Edit."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, cove_ved_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_cove_ved(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v124", now=TS)
    report = cove_ved_shaped_report(
        stele, consumer_scope="project:v124", now=TS
    )
    assert report["suite"] == "cove_ved_shaped"
    assert report["ok"] is True

    hall = stele.cove_hallucination(reduced=False)
    assert hall["apply"] is False

    know = stele.ved_knowledge(enhanced=False)
    assert know["apply"] is False
