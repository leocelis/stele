"""v15.7: QPiSSA + MoSLoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, qps_msl_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_qps_msl(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v157", now=TS)
    report = qps_msl_shaped_report(
        stele, consumer_scope="project:v157", now=TS
    )
    assert report["suite"] == "qps_msl_shaped"
    assert report["ok"] is True

    err = stele.qps_error(smaller_than_qlora=False)
    assert err["apply"] is False

    fuse = stele.msl_fuse(flexible_fuse=False)
    assert fuse["apply"] is False
