"""v13.9: QLoRA + AdaLoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, qlo_adl_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_qlo_adl(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v139", now=TS)
    report = qlo_adl_shaped_report(
        stele, consumer_scope="project:v139", now=TS
    )
    assert report["suite"] == "qlo_adl_shaped"
    assert report["ok"] is True

    mem = stele.qlo_memory(double_quant=False)
    assert mem["apply"] is False

    adaptive = stele.adl_adaptive(adaptive_rank=False)
    assert adaptive["apply"] is False
