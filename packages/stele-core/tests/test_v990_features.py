"""v9.9: Self-Ask + ReAct."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, selfask_react_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_selfask_react(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v99", now=TS)
    report = selfask_react_shaped_report(
        stele, consumer_scope="project:v99", now=TS
    )
    assert report["suite"] == "selfask_react_shaped"
    assert report["ok"] is True

    stop = stele.selfask_stop(enough=False)
    assert stop["apply"] is False

    act = stele.react_action(action="Lookup", arg="x")
    assert act["apply"] is False
