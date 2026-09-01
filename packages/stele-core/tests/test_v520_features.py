"""v5.2: AgentDoG trajectory diagnosis + MemWeaver dual-channel weave."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, agentdog_memweaver_shaped_report

TS = "2026-08-22T23:30:00Z"


def test_agentdog_memweaver(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v52", now=TS)
    report = agentdog_memweaver_shaped_report(
        stele, consumer_scope="project:v52", now=TS
    )
    assert report["suite"] == "agentdog_memweaver_shaped"
    assert report["ok"] is True

    tax = stele.taxonomy_inventory()
    assert tax["dimensions"] == 3
    assert "user_input" in tax["risk_sources"]
