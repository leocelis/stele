"""v0.1.4: model_id re-verify flags + one-hop LINK follow + dangling LINK report."""

from __future__ import annotations

from pathlib import Path

from helpers import TS, base_entry, oracle_evidence
from stele_core import Stele


def test_model_mismatch_flag_and_withhold(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="m", now=TS)
    eid = stele.add(
        base_entry(
            provenance={
                "agent": "agent-a",
                "task": "t",
                "environment": "e",
                "subject_id": "s",
                "source": "session:1",
                "written_at": TS,
                "model_id": "claude-old",
            }
        ),
        ts=TS,
    )["id"]
    stele.promote(eid, oracle_evidence(), actor="ci", ts=TS)

    flagged = stele.search(
        "cache",
        consumer_scope="project:demo",
        consumer_model_id="claude-new",
        model_policy="flag",
    )
    assert len(flagged) == 1 and flagged[0]["model_mismatch"] is True

    same = stele.search(
        "cache",
        consumer_scope="project:demo",
        consumer_model_id="claude-old",
    )
    assert same[0]["model_mismatch"] is False

    withheld = stele.search(
        "cache",
        consumer_scope="project:demo",
        consumer_model_id="claude-new",
        model_policy="withhold",
    )
    assert withheld == []


def test_follow_links_one_hop(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="l", now=TS)
    goal = stele.add(
        base_entry(
            layer="goal",
            title="Preserve midnight rollover safety",
            body="Upstream objective: stop cross-midnight key reuse.",
        ),
        ts=TS,
    )["id"]
    lesson = stele.add(
        base_entry(
            title="Pin cache keys to calendar buckets",
            body="Day-scoped cache keys prevent stale cross-day reads after midnight.",
        ),
        ts=TS,
    )["id"]
    stele.promote(goal, oracle_evidence(issuer="g"), actor="g", ts=TS)
    stele.promote(lesson, oracle_evidence(issuer="l"), actor="l", ts=TS)
    stele.link(lesson, kind="entry", ref=goal, actor="ops", ts=TS)

    plain = stele.search("calendar buckets cache keys", consumer_scope="project:demo")
    assert {s["id"] for s in plain} == {lesson}

    expanded = stele.search(
        "calendar buckets cache keys",
        consumer_scope="project:demo",
        follow_links=True,
    )
    ids = {s["id"] for s in expanded}
    assert lesson in ids and goal in ids
    via = [s for s in expanded if s["id"] == goal][0]
    assert via["via_link"] is True and via["linked_from"] == lesson


def test_reflect_reports_dangling_entry_links(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="d", now=TS)
    eid = stele.add(base_entry(), ts=TS)["id"]
    stele.promote(eid, oracle_evidence(), actor="ci", ts=TS)
    stele.link(eid, kind="entry", ref="missing-entry-id", actor="ops", ts=TS)
    report = stele.reflect(actor="ops", ts=TS)
    assert any(
        d["from"] == eid and d["ref"] == "missing-entry-id"
        for d in report["dangling_links"]
    )
