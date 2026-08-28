"""v15.6: OLoRA + LoRA-SP."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, olr_lsp_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_olr_lsp(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v156", now=TS)
    report = olr_lsp_shaped_report(
        stele, consumer_scope="project:v156", now=TS
    )
    assert report["suite"] == "olr_lsp_shaped"
    assert report["ok"] is True

    stable = stele.olr_stable(stable_landscape=False)
    assert stable["apply"] is False

    memory = stele.lsp_memory(lower_memory=False)
    assert memory["apply"] is False
