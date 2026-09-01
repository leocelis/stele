"""v10.4: Algorithm of Thoughts + Reasoning via Planning."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, aot_rap_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_aot_rap(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v104", now=TS)
    report = aot_rap_shaped_report(
        stele, consumer_scope="project:v104", now=TS
    )
    assert report["suite"] == "aot_rap_shaped"
    assert report["ok"] is True

    tunnel = stele.aot_tunnel_vision(activate=False)
    assert tunnel["apply"] is False

    select = stele.rap_select_path(visits=3)
    assert select["apply"] is False
