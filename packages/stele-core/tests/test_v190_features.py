"""v1.9: journal chain, spread_activate, density, retention."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, soda_synapse_shaped_report

TS = "2026-08-20T23:55:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v19",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def _entry(title: str) -> dict:
    return {
        "layer": "failure_lesson",
        "title": title,
        "body": f"{title} body with enough tokens for activation tests.",
        "scope": "project:v19",
        "temporal": {"valid_from": TS, "last_verified": TS},
        "provenance": {
            "agent": "agent",
            "task": "t",
            "environment": "local",
            "subject_id": "subj-v19",
            "source": "session:ok",
            "written_at": TS,
        },
    }


def test_journal_chain(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="chain", now=TS)
    stele.add(_entry("Chain tip"), ts=TS)
    report = stele.verify_journal_chain()
    assert report["ok"] is True
    assert report["chained_rows"] >= 1
    head = stele.journal_chain_head()
    assert head["head"] == report["head"]


def test_spread_density_retention(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="act", now=TS)
    a = stele.add(_entry("Anchor tip"), ts=TS)["id"]
    b = stele.add(_entry("Neighbor tip"), ts=TS)["id"]
    stele.promote(a, EV, actor="ci", ts=TS)
    stele.promote(b, EV, actor="ci", ts=TS)
    stele.link(a, kind="entry", ref=b, actor="ops", ts=TS)
    spread = stele.spread_activate([a], max_hops=2)
    ids = {x["id"] for x in spread["activations"]}
    assert a in ids and b in ids
    dens = stele.connection_density(a)
    assert dens["degree"] == 1
    ret = stele.retention_score(a, now=TS)
    assert ret["retention_score"] > 0
    hits = stele.search("tip", consumer_scope="project:v19", prefer_dense=True)
    assert hits and "connection_density" in hits[0]


def test_soda_synapse_shaped_report(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="harness", now=TS)
    report = soda_synapse_shaped_report(stele, consumer_scope="project:demo", now=TS)
    assert report["suite"] == "soda_synapse_shaped"
    assert report["ok"] is True
