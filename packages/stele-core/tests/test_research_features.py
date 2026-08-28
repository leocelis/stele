"""Research-backed feature tests: distill gate, env check, export, harness, migration."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from helpers import TS, base_entry, oracle_evidence
from stele_core import (
    LessonTask,
    SchemaError,
    Stele,
    compare_with_without,
    migration_entry,
)


def test_rejects_raw_transcript_on_add(stele: Stele) -> None:
    transcript = "\n".join(
        [
            "User: how do I fix cache?",
            "Assistant: try this",
            "User: still broken",
            "Assistant: try that",
            "User: ok",
            "Assistant: done",
            "User: thanks",
            "Assistant: np",
        ]
    )
    with pytest.raises(SchemaError, match="transcript"):
        stele.add(base_entry(body=transcript), ts=TS)


def test_rejects_tool_trajectory_dump(stele: Stele) -> None:
    body = (
        "Action: search\nObservation: x\n"
        "Action: edit\nObservation: y\n"
        "tool_call: foo\nfunction_call: bar\n"
        "Action: done\nObservation: z"
    )
    with pytest.raises(SchemaError, match="trajectory"):
        stele.add(base_entry(body=body), ts=TS)


def test_empty_query_returns_empty(stele: Stele) -> None:
    eid = stele.add(base_entry(), ts=TS)["id"]
    stele.promote(eid, oracle_evidence(), actor="ci", ts=TS)
    assert stele.search("", consumer_scope="project:demo") == []
    assert stele.search("   ", consumer_scope="project:demo") == []


def test_env_mismatch_flag_on_workflow(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="env", now=TS)
    eid = stele.add(
        base_entry(
            layer="workflow",
            title="Rotate cache keys",
            body="Use day-scoped keys; verify after deploy.",
            env_assumptions=["linux", "redis>=7"],
        ),
        ts=TS,
    )["id"]
    stele.promote(eid, oracle_evidence(), actor="ci", ts=TS)

    ok = stele.search(
        "cache keys",
        consumer_scope="project:demo",
        consumer_env=["linux", "redis>=7"],
    )
    assert ok[0]["env_mismatch"] is False

    bad = stele.search(
        "cache keys",
        consumer_scope="project:demo",
        consumer_env=["windows"],
    )
    assert bad[0]["env_mismatch"] is True
    assert "linux" in bad[0]["missing_env_assumptions"]


def test_export_subject_allowlist_and_adaptation(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="ex", now=TS)
    a = stele.add(
        base_entry(
            title="Allowed subject lesson",
            body="Day buckets. Also had: $ npm install leftpad",
            provenance={
                "agent": "a",
                "task": "t",
                "environment": "e",
                "subject_id": "keep-me",
                "source": "session:1",
                "written_at": TS,
            },
        ),
        ts=TS,
    )["id"]
    b = stele.add(
        base_entry(
            title="Other subject lesson",
            body="Unrelated subject content about cache.",
            provenance={
                "agent": "a",
                "task": "t",
                "environment": "e",
                "subject_id": "drop-me",
                "source": "session:2",
                "written_at": TS,
            },
        ),
        ts=TS,
    )["id"]
    stele.promote(a, oracle_evidence(issuer="c1"), actor="c1", ts=TS)
    stele.promote(b, oracle_evidence(issuer="c2"), actor="c2", ts=TS)

    dest = tmp_path / "pack"
    manifest = stele.export(
        dest,
        scope="project:demo",
        audience="practitioner",
        purpose="share",
        created_at=TS,
        expiry="2027-01-01T00:00:00Z",
        subject_allowlist=["keep-me"],
    )
    assert manifest["entry_count"] == 1
    assert manifest["may_be_outdated"] is True
    adaptation = json.loads((dest / "adaptation.json").read_text())
    assert "re_derive" in adaptation
    assert any("npm install" in x for x in adaptation["re_derive"])
    body = json.loads(next((dest / "entries").glob("*.json")).read_text())["body"]
    assert "npm install" not in body


def test_migration_producer_quarantines(stele: Stele) -> None:
    payload = migration_entry(
        {
            "layer": "failure_lesson",
            "title": "Migrated cache lesson",
            "body": "Day-scoped keys from old feedback file.",
        },
        written_at=TS,
        project="demo",
        source_pointer="feedback:redacted:cache.yaml",
    )
    assert payload["provenance"]["agent"] == "migration"
    added = stele.add(payload, ts=TS)
    assert added["state"] == "quarantined"
    with pytest.raises(SchemaError, match="redacted|private"):
        migration_entry(
            {"layer": "goal", "title": "x", "body": "y"},
            written_at=TS,
            project="demo",
            source_pointer="ledger/tenants/private/feedback/x.yaml",
        )


def test_task_outcome_harness_with_vs_without(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="eval", now=TS)
    eid = stele.add(
        base_entry(
            title="Cache day bucket insight",
            body="Pin cache keys to calendar day buckets to stop stale cross-day reads.",
        ),
        ts=TS,
    )["id"]
    stele.promote(eid, oracle_evidence(), actor="ci", ts=TS)

    def needs_day_bucket(slices):  # type: ignore[no-untyped-def]
        text = " ".join(f"{s['title']} {s['body']}" for s in slices).lower()
        return "day" in text and "bucket" in text

    tasks = [
        LessonTask(
            task_id="cache-stale",
            query="stale cross-day cache reads",
            consumer_scope="project:demo",
            needs=needs_day_bucket,
        ),
        LessonTask(
            task_id="unrelated",
            query="quantum entanglement protocols",
            consumer_scope="project:demo",
            needs=needs_day_bucket,
        ),
    ]
    report = compare_with_without(tasks, stele)
    assert report["n"] == 2
    assert report["without_stele_rate"] == 0.0
    assert report["with_stele_rate"] == 0.5  # only cache-stale finds the lesson
    assert report["lift"] == 0.5
    assert report["tasks"][0]["memory_helped"] is True
    assert report["tasks"][1]["memory_helped"] is False
