"""v18.6: NLoRA + ROSA random subspace."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, nlr_rsa_shaped_report

TS = "2026-08-22T12:00:00Z"


def test_nlr_rsa(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v186", now=TS)
    report = nlr_rsa_shaped_report(
        stele, consumer_scope="project:v186", now=TS
    )
    assert report["suite"] == "nlr_rsa_shaped"
    assert report["ok"] is True

    cheap = stele.nlr_cheap(cheaper_svd=False)
    assert cheap["apply"] is False

    express = stele.rsa_express(more_expressive=False)
    assert express["apply"] is False
