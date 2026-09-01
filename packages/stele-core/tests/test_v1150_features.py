"""v11.5: Auto-CoT + CAMEL."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, autocot_camel_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_autocot_camel(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v115", now=TS)
    report = autocot_camel_shaped_report(
        stele, consumer_scope="project:v115", now=TS
    )
    assert report["suite"] == "autocot_camel_shaped"
    assert report["ok"] is True

    done = stele.camel_complete(done=False)
    assert done["apply"] is False

    loop = stele.autocot_loop_plan(phase="cluster")
    assert loop["apply"] is False
