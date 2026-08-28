"""v0.1.3 features: stale withhold, reviewer slice, verify, pack transfer eval."""

from __future__ import annotations

from pathlib import Path

from helpers import TS, base_entry, oracle_evidence
from stele_core import (
    LessonTask,
    Stele,
    foreign_pack_transfer_eval,
    insight_needs,
)


def test_stale_policy_withhold(tmp_path: Path) -> None:
    stele = Stele.open(
        tmp_path / "s",
        store_id="stale",
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

    flagged = stele.search("cache", consumer_scope="project:demo", stale_policy="flag")
    assert len(flagged) == 1 and flagged[0]["stale"] is True

    withheld = stele.search(
        "cache", consumer_scope="project:demo", stale_policy="withhold"
    )
    assert withheld == []


def test_verify_store_ok_and_detects_dual(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v", now=TS)
    eid = stele.add(base_entry(), ts=TS)["id"]
    stele.promote(eid, oracle_evidence(), actor="ci", ts=TS)
    report = stele.verify()
    assert report["ok"] is True
    assert report["entry_count"] == 1
    assert report["errors"] == []

    # Corrupt: copy promoted entry into quarantine (dual location)
    src = stele.store.entries_p / f"{eid}.json"
    dst = stele.store.entries_q / f"{eid}.json"
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    bad = stele.verify()
    assert bad["ok"] is False
    assert any("quarantine and promoted" in e for e in bad["errors"])


def test_reviewer_corrections_bounded(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="rev", now=TS)
    ids = []
    for i in range(5):
        eid = stele.add(
            base_entry(
                title=f"Lesson {i} about cache buckets",
                body=f"Day-scoped keys insight number {i}.",
            ),
            ts=TS,
        )["id"]
        stele.promote(eid, oracle_evidence(issuer=f"ci{i}"), actor=f"ci{i}", ts=TS)
        ids.append(eid)
    slice_ = stele.reviewer_corrections(limit=3)
    assert len(slice_) == 3
    assert all(s["kind"] == "promoted" for s in slice_)


def test_foreign_pack_transfer_eval(tmp_path: Path) -> None:
    donor = Stele.open(tmp_path / "donor", store_id="donor", now=TS)
    eid = donor.add(
        base_entry(
            title="Donor cache day bucket insight",
            body="Pin cache keys to calendar day buckets to stop stale reads.",
        ),
        ts=TS,
    )["id"]
    donor.promote(eid, oracle_evidence(), actor="ci", ts=TS)

    recipient = Stele.open(tmp_path / "recv", store_id="recv", now=TS)
    tasks = [
        LessonTask(
            task_id="use-donor-lesson",
            query="stale cache day buckets",
            consumer_scope="project:demo",
            needs=insight_needs("day", "bucket"),
        )
    ]
    # Before hydrate, recipient fails
    assert recipient.search("day bucket", consumer_scope="project:demo") == []

    report = foreign_pack_transfer_eval(
        donor,
        recipient,
        tasks,
        pack_dir=tmp_path / "pack",
        scope="project:demo",
        created_at=TS,
        expiry="2027-01-01T00:00:00Z",
        promote_actor="import-oracle",
        promote_evidence=[
            {
                "type": "human_signoff",
                "issuer": "import-oracle",
                "ref": "pack-review",
                "observed_at": TS,
                "verdict": "supports",
            }
        ],
    )
    assert report["before_hydrate"]["with_stele_rate"] == 0.0
    assert report["after_hydrate"]["with_stele_rate"] == 1.0
    assert report["transfer_lift"] == 1.0
    assert recipient.verify()["ok"] is True
