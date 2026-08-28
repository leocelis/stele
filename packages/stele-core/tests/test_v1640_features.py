"""v16.4: LoRAMoE + MoELoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, lme_mel_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_lme_mel(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v164", now=TS)
    report = lme_mel_shaped_report(
        stele, consumer_scope="project:v164", now=TS
    )
    assert report["suite"] == "lme_mel_shaped"
    assert report["ok"] is True

    forget = stele.lme_forget(preserves_world=False)
    assert forget["apply"] is False

    sparse = stele.mel_sparse(sparse_activate=False)
    assert sparse["apply"] is False
