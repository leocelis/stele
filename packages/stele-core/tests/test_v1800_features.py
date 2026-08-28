"""v18.0: Q-GaLore + LoRA-Flow."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, qga_lfw_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_qga_lfw(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v180", now=TS)
    report = qga_lfw_shaped_report(
        stele, consumer_scope="project:v180", now=TS
    )
    assert report["suite"] == "qga_lfw_shaped"
    assert report["ok"] is True

    mem = stele.qga_mem(consumer_gpu=False)
    assert mem["apply"] is False

    few = stele.lfw_few(few_shot=False)
    assert few["apply"] is False
