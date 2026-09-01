"""v3.9: Governed Memory deepen + HyMem typed isolation."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, govmem_hymem_shaped_report

TS = "2026-08-21T00:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v39",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def test_govmem_hymem(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v39", now=TS)
    a = stele.add(
        {
            "layer": "workflow",
            "title": "Payment backoff policy",
            "body": "Retries must use exponential backoff. Cap at five attempts.",
            "scope": "project:v39",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "oracle",
                "task": "a",
                "environment": "local",
                "subject_id": "subj-alpha",
                "source": "oracle:gate",
                "written_at": TS,
            },
            "usage": {"helpful": 3, "harmful": 0, "pinned": True},
            "env_assumptions": ["local", "pytest"],
        },
        ts=TS,
    )["id"]
    stele.promote(a, EV, actor="ci", ts=TS)
    b = stele.add(
        {
            "layer": "decision",
            "title": "Other tenant secret",
            "body": "Never share subject beta webhook tokens across tenants.",
            "scope": "project:v39",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "oracle",
                "task": "b",
                "environment": "local",
                "subject_id": "subj-beta",
                "source": "oracle:gate",
                "written_at": TS,
            },
            "usage": {"helpful": 2, "harmful": 0},
        },
        ts=TS,
    )["id"]
    stele.promote(b, EV, actor="ci", ts=TS)

    dual = stele.dual_project(a)
    assert dual["fact_count"] >= 1
    assert dual["typed_properties"]["subject_id"] == "subj-alpha"

    route = stele.governance_route("payment webhook backoff retries")
    assert route["ok"] is True
    assert route["count"] >= 1
    assert route["path"] == "fast_hybrid"

    stele.session_delta_open("sess-1")
    d1 = stele.session_delta_deliver("sess-1", route)
    d2 = stele.session_delta_deliver("sess-1", route)
    assert d1["inject_count"] >= 1
    if any(r.get("tier") == "critical" for r in route["selected"]):
        assert d2["skipped_count"] >= 1
    assert stele.session_delta_status("sess-1")["ok"] is True

    ctx = stele.entity_context("subj-alpha")
    assert ctx["ok"] is True
    assert ctx["entry_count"] >= 1

    leak = stele.entity_leak_probe(
        "subj-alpha", query="webhook", consumer_scope="project:v39"
    )
    assert leak["ok"] is True

    raw = stele.entity_leak_probe(
        "subj-alpha",
        query="webhook",
        consumer_scope="project:v39",
        prefilter=False,
    )
    assert raw["leak_count"] >= 1 or raw["ok"] is False

    assert stele.hymem_classify_slot("run shell tool execute stdout")["slot"] == "execute"
    pack = stele.hymem_isolate_pack(
        [
            {"text": "plan next step for payment goal"},
            {"text": "run shell tool execute stdout"},
            {"text": "remember prior workflow lesson"},
        ]
    )
    assert pack["ok"] is True
    assert pack["dilution_ok"] is True


def test_harness_v39(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "h", store_id="h", now=TS)
    report = govmem_hymem_shaped_report(
        stele, consumer_scope="project:demo", now=TS
    )
    assert report["suite"] == "govmem_hymem_shaped"
    assert report["ok"] is True
