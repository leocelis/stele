"""v15.3: MiLoRA + CorDA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, mil_cda_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_mil_cda(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v153", now=TS)
    report = mil_cda_shaped_report(
        stele, consumer_scope="project:v153", now=TS
    )
    assert report["suite"] == "mil_cda_shaped"
    assert report["ok"] is True

    preserve = stele.mil_preserve(preserves_principal=False)
    assert preserve["apply"] is False

    forget = stele.cda_forget(less_forgetting=False)
    assert forget["apply"] is False

    ipm = stele.cda_mode(cov_id="x", mode="IPM")
    assert ipm["mode"] == "IPM"
