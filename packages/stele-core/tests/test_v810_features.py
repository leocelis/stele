"""v8.1: O-Mem + Mandol."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, omem_mandol_shaped_report

TS = "2026-08-24T03:00:00Z"


def test_omem_mandol(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v81", now=TS)
    report = omem_mandol_shaped_report(
        stele, consumer_scope="project:v81", now=TS
    )
    assert report["suite"] == "omem_mandol_shaped"
    assert report["ok"] is True

    reject = stele.omem_profile_gate(confidence=0.2, min_confidence=0.5)
    assert reject["admit"] is False

    over = stele.mandol_token_budget(selected_tokens=900, max_tokens=512)
    assert over["under_budget"] is False
