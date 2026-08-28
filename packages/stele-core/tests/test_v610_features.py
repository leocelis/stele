"""v6.1: ReMe + Dynamic Cheatsheet."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, reme_cheatsheet_shaped_report

TS = "2026-08-23T07:00:00Z"


def test_reme_cheatsheet(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v61", now=TS)
    report = reme_cheatsheet_shaped_report(
        stele, consumer_scope="project:v61", now=TS
    )
    assert report["suite"] == "reme_cheatsheet_shaped"
    assert report["ok"] is True

    prune = stele.utility_prune_plan(
        [{"experience_id": "x", "freq": 4, "utility": 0}], alpha=3, beta=0.3
    )
    assert prune["prune_count"] == 1
    order = stele.dc_rs_order_check(["retrieve", "curate", "generate"])
    assert order["mode"] == "DC-RS"
