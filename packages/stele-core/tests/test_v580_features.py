"""v5.8: MemSkill skill bank + Memory-R1 ADD/UPDATE/DELETE/NOOP."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, memskill_memoryr1_shaped_report

TS = "2026-08-23T04:00:00Z"


def test_memskill_memoryr1(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v58", now=TS)
    report = memskill_memoryr1_shaped_report(
        stele, consumer_scope="project:v58", now=TS
    )
    assert report["suite"] == "memskill_memoryr1_shaped"
    assert report["ok"] is True

    bank = stele.init_skill_bank()
    assert bank["skill_count"] >= 4
    op = stele.classify_memory_op("totally novel zebra fact")
    assert op["op"] == "ADD"
