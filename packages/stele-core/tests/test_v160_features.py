"""v1.6: store_seal, verify_seal, attribution_receipt, replay_consistency, memmark report."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, memmark_shaped_report
from stele_core.integrity import entry_content_digest

TS = "2026-08-20T23:00:00Z"


def _entry(title: str = "Day tip") -> dict:
    return {
        "layer": "failure_lesson",
        "title": title,
        "body": "Day-scoped keys prevent stale cross-day reads after midnight.",
        "scope": "project:v16",
        "temporal": {"valid_from": TS, "last_verified": TS},
        "provenance": {
            "agent": "agent",
            "task": "t",
            "environment": "local",
            "subject_id": "subj-v16",
            "source": "session:ok",
            "written_at": TS,
        },
    }


def test_seal_roundtrip_and_tamper(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="seal", now=TS)
    eid = stele.add(_entry(), ts=TS)["id"]
    seal = stele.store_seal()
    assert seal["entry_count"] == 1
    assert stele.verify_seal(seal)["ok"] is True
    entry = stele.store.read_entry(eid)
    assert entry_content_digest(entry) == seal["entries"][0]["content_digest"]
    stele.update(eid, {"title": "Day tip mutated"}, actor="ops", ts=TS)
    assert stele.verify_seal(seal)["ok"] is False


def test_attribution_receipt_and_replay(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="attr", now=TS)
    eid = stele.add(_entry("Receipt tip"), ts=TS)["id"]
    receipt = stele.attribution_receipt(eid)
    assert receipt["present"] is True
    assert receipt["content_digest"]
    assert any(j["op"] == "ADD" for j in receipt["journal"])
    replay = stele.replay_consistency()
    assert replay["ok"] is True


def test_memmark_shaped_report(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="mm", now=TS)
    report = memmark_shaped_report(stele, now=TS)
    assert report["suite"] == "memmark_shaped"
    assert report["ok"] is True
    assert report["tamper_detect"]["ok"] is True
