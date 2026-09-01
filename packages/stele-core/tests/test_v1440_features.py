"""v14.4: LoRA-XS + AsymmetryLoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, lxs_asy_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_lxs_asy(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v144", now=TS)
    report = lxs_asy_shaped_report(
        stele, consumer_scope="project:v144", now=TS
    )
    assert report["suite"] == "lxs_asy_shaped"
    assert report["ok"] is True

    tiny = stele.lxs_tiny(r_squared_only=False)
    assert tiny["apply"] is False

    bound = stele.asy_bound(tighter_bound=False)
    assert bound["apply"] is False
