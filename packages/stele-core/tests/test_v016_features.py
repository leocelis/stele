"""v0.1.6 living ledger: outcomes, pin, match_reasons, compress, stale, reverify, related."""

from __future__ import annotations

from pathlib import Path

from helpers import TS, base_entry, oracle_evidence
from stele_core import Stele


def test_record_outcome_and_prefer_helpful(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="o", now=TS)
    a = stele.add(
        base_entry(title="Alpha cache day bucket tip", body="Day buckets for alpha."),
        ts=TS,
    )["id"]
    b = stele.add(
        base_entry(title="Beta cache day bucket tip", body="Day buckets for beta."),
        ts=TS,
    )["id"]
    stele.promote(a, oracle_evidence(issuer="cia"), actor="cia", ts=TS)
    stele.promote(b, oracle_evidence(issuer="cib"), actor="cib", ts=TS)
    stele.record_outcome(b, "helpful", actor="consumer", ts=TS)
    stele.pin(b, actor="ops", ts=TS)

    hits = stele.search("day bucket", consumer_scope="project:demo", prefer_helpful=True)
    assert hits[0]["id"] == b
    assert hits[0]["usage"]["helpful"] == 1
    assert hits[0]["usage"]["pinned"] is True
    assert any(r.startswith("terms:") for r in hits[0]["match_reasons"])


def test_body_max_chars_compress(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="c", now=TS)
    long_body = "Day bucket " + ("x" * 200)
    eid = stele.add(base_entry(body=long_body), ts=TS)["id"]
    stele.promote(eid, oracle_evidence(), actor="ci", ts=TS)
    hits = stele.search("bucket", consumer_scope="project:demo", body_max_chars=40)
    assert hits[0]["body_truncated"] is True
    assert hits[0]["body"].endswith("…")
    assert len(hits[0]["body"]) <= 41


def test_stale_report_and_reverify(tmp_path: Path) -> None:
    stele = Stele.open(
        tmp_path / "s",
        store_id="st",
        now=TS,
        staleness_horizon="2026-08-19T00:00:00Z",
    )
    eid = stele.add(
        base_entry(
            temporal={
                "valid_from": "2026-01-01T00:00:00Z",
                "last_verified": "2026-01-01T00:00:00Z",
            },
            provenance={
                "agent": "agent-a",
                "task": "t",
                "environment": "e",
                "subject_id": "s",
                "source": "session:1",
                "written_at": "2026-01-01T00:00:00Z",
            },
        ),
        ts=TS,
    )["id"]
    stele.promote(eid, oracle_evidence(), actor="ci", ts="2026-01-01T00:00:00Z")
    report = stele.stale_report(now=TS)
    assert any(r["id"] == eid for r in report)

    stele.reverify(
        [eid],
        [
            {
                "type": "human_signoff",
                "issuer": "reverify-oracle",
                "ref": "batch-1",
                "observed_at": TS,
                "verdict": "supports",
            }
        ],
        actor="reverify-oracle",
        ts=TS,
    )
    # After reverify with now as last_verified and horizon before now, still stale
    # unless we raise horizon — set last_verified to TS which is AFTER horizon → not stale
    report2 = stele.stale_report(now=TS)
    assert not any(r["id"] == eid for r in report2)


def test_related_inbound_outbound(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="rel", now=TS)
    goal = stele.add(
        base_entry(
            layer="goal",
            title="Preserve midnight safety",
            body="Stop cross-midnight key reuse.",
        ),
        ts=TS,
    )["id"]
    lesson = stele.add(base_entry(), ts=TS)["id"]
    stele.promote(goal, oracle_evidence(issuer="g"), actor="g", ts=TS)
    stele.promote(lesson, oracle_evidence(issuer="l"), actor="l", ts=TS)
    stele.link(lesson, kind="entry", ref=goal, actor="ops", ts=TS)
    nb = stele.related(goal)
    assert any(x["from"] == lesson for x in nb["inbound"])
    nb2 = stele.related(lesson)
    assert any(x["ref"] == goal for x in nb2["outbound"])
