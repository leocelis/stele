"""v18.15: SDT + MEFT."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, sdt_mef_shaped_report

TS = "2026-08-28T12:00:00Z"


def test_sdt_mef(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v1815", now=TS)
    report = sdt_mef_shaped_report(
        stele, consumer_scope="project:v1815", now=TS
    )
    assert report["suite"] == "sdt_mef_shaped"
    assert report["ok"] is True

    ssm = stele.sdt_ssm(ssm_only=False)
    assert ssm["apply"] is False

    cpu = stele.mef_cpu(cpu_offload=False)
    assert cpu["apply"] is False
