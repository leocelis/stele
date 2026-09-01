"""v1.0 features: schema export, snapshot, doctor, memorywire projection, CLI."""

from __future__ import annotations

import json
from pathlib import Path

from stele_core import (
    Stele,
    entry_json_schema,
    from_memorywire_recall_hits,
    to_memorywire_remember,
)
from stele_core.cli import main

TS = "2026-08-20T15:00:00Z"


def _lesson(title: str = "Pin cache keys") -> dict:
    return {
        "layer": "failure_lesson",
        "title": title,
        "body": "Day-scoped keys prevent stale cross-day reads after midnight.",
        "scope": "project:v1",
        "temporal": {"valid_from": TS, "last_verified": TS},
        "provenance": {
            "agent": "v1-agent",
            "task": "cache",
            "environment": "local",
            "subject_id": "subj-v1",
            "source": "session:v1",
            "written_at": TS,
        },
    }


def test_entry_json_schema_exports_contract() -> None:
    schema = entry_json_schema()
    assert schema["$schema"].endswith("2020-12/schema")
    assert "body" in schema["properties"]
    assert "failure_lesson" in schema["properties"]["layer"]["enum"]
    assert schema["properties"]["schema_version"]["const"] == 1


def test_snapshot_and_doctor(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "store", store_id="snap", now=TS)
    added = stele.add(_lesson(), ts=TS)
    stele.promote(
        added["id"],
        [
            {
                "type": "test_result",
                "issuer": "ci",
                "ref": "t",
                "observed_at": TS,
                "verdict": "supports",
                "command": "pytest -q",
                "exit_status": 0,
            }
        ],
        actor="ci",
        ts=TS,
    )
    dest = tmp_path / "backup"
    snap = stele.snapshot(dest, actor="ops", ts=TS)
    assert snap["entries"] == 1
    assert (dest / "stele.json").exists()
    assert (dest / "entries" / "promoted" / f"{added['id']}.json").exists()
    assert not (dest / "index").exists()

    report = stele.doctor(now=TS)
    assert report["ok"] is True
    assert report["stats"]["total"] == 1


def test_memorywire_projection() -> None:
    entry = {
        **_lesson(),
        "id": "se_0123456789abcdef",
        "schema_version": 1,
        "state": "promoted",
    }
    remember = to_memorywire_remember(entry)
    assert remember["op"] == "remember"
    assert remember["type"] == "episodic"
    assert "Day-scoped" in remember["content"]
    assert remember["metadata"]["stele_id"] == "se_0123456789abcdef"

    stubs = from_memorywire_recall_hits(
        [
            {
                "content": "x",
                "score": 0.9,
                "metadata": {"stele_id": "se_0123456789abcdef", "title": "t"},
            }
        ]
    )
    assert stubs[0]["id"] == "se_0123456789abcdef"
    assert stubs[0]["foreign"] is False
    foreign = from_memorywire_recall_hits([{"content": "y", "metadata": {}}])
    assert foreign[0]["foreign"] is True


def test_cli_schema_doctor_snapshot(tmp_path: Path) -> None:
    store = tmp_path / "s"
    stele = Stele.open(store, store_id="cli", now=TS)
    stele.add(_lesson(), ts=TS)
    assert main(["schema"]) == 0
    out = tmp_path / "entry.schema.json"
    assert main(["schema", "--out", str(out)]) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["title"] == "SteleEntry"
    assert main(["doctor", str(store), "--now", TS]) == 0
    dest = tmp_path / "snap"
    assert main(["snapshot", str(store), str(dest), "--now", TS, "--actor", "cli"]) == 0
    assert (dest / "stele.json").exists()
