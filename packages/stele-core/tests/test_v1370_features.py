"""v13.7: Compacter + (IA)^3."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, cmp_ia3_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_cmp_ia3(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v137", now=TS)
    report = cmp_ia3_shaped_report(
        stele, consumer_scope="project:v137", now=TS
    )
    assert report["suite"] == "cmp_ia3_shaped"
    assert report["ok"] is True

    compact = stele.cmp_compact(param_efficient=False)
    assert compact["apply"] is False

    mixed = stele.ia3_mixed(mixed_batch=False)
    assert mixed["apply"] is False
