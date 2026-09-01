"""v11.2: Voyager + ReWOO."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, voy_rewoo_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_voy_rewoo(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v112", now=TS)
    report = voy_rewoo_shaped_report(
        stele, consumer_scope="project:v112", now=TS
    )
    assert report["suite"] == "voy_rewoo_shaped"
    assert report["ok"] is True

    ver = stele.voy_self_verify(skill_id="abc", passed=False)
    assert ver["apply"] is False

    tok = stele.rewoo_token_save(reduced=False)
    assert tok["apply"] is False
