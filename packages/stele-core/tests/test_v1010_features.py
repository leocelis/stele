"""v10.1: Reflexion + Self-Consistency."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, reflexion_selfcons_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_reflexion_selfcons(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v101", now=TS)
    report = reflexion_selfcons_shaped_report(
        stele, consumer_scope="project:v101", now=TS
    )
    assert report["suite"] == "reflexion_selfcons_shaped"
    assert report["ok"] is True

    mem = stele.rx_memory_store(reflection_id="r1")
    assert mem["apply"] is False

    vote = stele.sc_majority_vote(votes={"a": 1, "b": 2})
    assert vote["winner"] == "b"
