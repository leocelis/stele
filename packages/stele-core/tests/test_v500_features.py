"""v5.0: persistence layers + credential reject + uncertainty gate."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, knowledgelayer_cred_uncertainty_shaped_report

TS = "2026-08-22T22:00:00Z"


def test_knowledgelayer_cred_uncertainty(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v50", now=TS)
    report = knowledgelayer_cred_uncertainty_shaped_report(
        stele, consumer_scope="project:v50", now=TS
    )
    assert report["suite"] == "knowledgelayer_cred_uncertainty_shaped"
    assert report["ok"] is True

    gate = stele.credential_reject_gate(
        candidate={
            "title": "tok",
            "body": "password=hunter2-super-secret",
        }
    )
    assert gate["decision"] == "reject"

    plan = stele.reasoning_reserve_plan(1000, confidence=0.2)
    assert plan["reasoning_fraction"] <= 0.15
