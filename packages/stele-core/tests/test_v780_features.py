"""v7.8: MemOS + SkillCraft."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, memos_skillcraft_shaped_report

TS = "2026-08-24T00:00:00Z"


def test_memos_skillcraft(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v78", now=TS)
    report = memos_skillcraft_shaped_report(
        stele, consumer_scope="project:v78", now=TS
    )
    assert report["suite"] == "memos_skillcraft_shaped"
    assert report["ok"] is True

    reject = stele.skillcraft_save_skill(
        name="bad", steps=2, verified=False
    )
    assert reject["admitted"] is False

    bad_fuse = stele.memos_fuse_gate(compatible=True, conflict=True)
    assert bad_fuse["fuse"] is False
