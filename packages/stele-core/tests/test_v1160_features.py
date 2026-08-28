"""v11.6: Chameleon + Recursion of Thought."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, cham_rot_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_cham_rot(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v116", now=TS)
    report = cham_rot_shaped_report(
        stele, consumer_scope="project:v116", now=TS
    )
    assert report["suite"] == "cham_rot_shaped"
    assert report["ok"] is True

    exe = stele.cham_execute(plan_id="abc")
    assert exe["apply"] is False

    lim = stele.rot_context_limit(within_limit=False)
    assert lim["apply"] is False
