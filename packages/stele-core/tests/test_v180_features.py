"""v1.8: blast_radius, merge_classify, path_trust, meld_map report."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, meld_map_shaped_report

TS = "2026-08-20T23:45:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v18",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def _entry(title: str, *, source: str = "session:ok", key: str | None = None) -> dict:
    e = {
        "layer": "failure_lesson",
        "title": title,
        "body": f"{title} body with enough tokens for retrieval and graph tests.",
        "scope": "project:v18",
        "temporal": {"valid_from": TS, "last_verified": TS},
        "provenance": {
            "agent": "agent",
            "task": "t",
            "environment": "local",
            "subject_id": "subj-v18",
            "source": source,
            "written_at": TS,
        },
    }
    if key:
        e["conflict_key"] = key
    return e


def test_merge_classify_and_blast(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="meld", now=TS)
    a = stele.add(_entry("API host is old", key="pref:host"), ts=TS)["id"]
    b = stele.add(_entry("API host is new", key="pref:host"), ts=TS)["id"]
    c = stele.add(_entry("Backoff tip"), ts=TS)["id"]
    for eid in (a, b, c):
        stele.promote(eid, EV, actor="ci", ts=TS)
    stele.link(a, kind="entry", ref=c, actor="ops", ts=TS)
    out = stele.merge_classify(a, b)
    assert out["outcome"] in {"merge", "conflict"}
    radius = stele.blast_radius(a, max_depth=2)
    assert c in radius["ids"]


def test_path_trust_filter(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="map", now=TS)
    good = stele.add(_entry("Trusted tip host", source="session:trusted"), ts=TS)["id"]
    bad = stele.add(_entry("Shadow tip host", source="session:shadow"), ts=TS)["id"]
    stele.promote(good, EV, actor="ci", ts=TS)
    stele.promote(bad, EV, actor="ci", ts=TS)
    tg = stele.path_trust(good, trusted_sources=["session:trusted"])
    tb = stele.path_trust(bad, trusted_sources=["session:trusted"])
    assert tg["path_trust"] > tb["path_trust"]
    hits = stele.search(
        "host",
        consumer_scope="project:v18",
        min_path_trust=0.9,
        trusted_sources_for_trust=["session:trusted"],
    )
    assert {h["id"] for h in hits} == {good}


def test_meld_map_shaped_report(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="harness", now=TS)
    report = meld_map_shaped_report(stele, consumer_scope="project:demo", now=TS)
    assert report["suite"] == "meld_map_shaped"
    assert report["ok"] is True
