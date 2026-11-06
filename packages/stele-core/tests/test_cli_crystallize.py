"""Each crystallize subcommand runs its own handler.

Two functions shared the name cmd_crystallize, so the second replaced the first
and `crystallize-skill` crashed with AttributeError on args.plan_id.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from helpers import TS
from stele_core import Stele, himem_hmeml_shaped_report
from stele_core.cli import main


@pytest.mark.parametrize(
    "argv",
    [
        ["crystallize-skill", "{store}", "missing-id", "--now", TS, "--actor", "ops"],
        ["crystallize", "{store}", "plan-1", "2", "--now", TS],
    ],
    ids=["skill", "plan"],
)
def test_crystallize_commands_do_not_share_a_handler(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], argv: list[str]
) -> None:
    store = tmp_path / "s"
    Stele.open(store, store_id="cli", now=TS)
    code = main([a.replace("{store}", str(store)) for a in argv])
    assert code in {0, 1}
    assert capsys.readouterr().out.strip()


def test_report_keeps_both_the_note_check_and_the_note(tmp_path: Path) -> None:
    """A repeated dict key silently dropped the note check from this report."""
    report = himem_hmeml_shaped_report(Stele.open(tmp_path / "s", store_id="n", now=TS))
    assert isinstance(report["note"], str)
    assert report["note_check"] == {"ok": True}
