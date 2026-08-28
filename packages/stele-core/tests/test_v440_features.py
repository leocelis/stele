"""v4.4: TGMS plan/claim/quarantine + MemoryData localized maintenance."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, tgms_memdata_shaped_report

TS = "2026-08-21T18:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v44",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def _promote(stele: Stele, title: str, body: str, ck: str) -> str:
    eid = stele.add(
        {
            "layer": "decision",
            "title": title,
            "body": body,
            "scope": "project:v44",
            "conflict_key": ck,
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "oracle",
                "task": "v44",
                "environment": "local",
                "subject_id": "s",
                "source": "oracle:v44",
                "written_at": TS,
            },
        },
        ts=TS,
    )["id"]
    stele.promote(eid, EV, actor="ci", ts=TS)
    return eid


def test_tgms_memdata(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v44", now=TS)
    a = _promote(
        stele,
        "Retry backoff",
        "Payment retries use exponential backoff and cap at five.",
        "policy:retry",
    )
    b = _promote(
        stele,
        "Retry backoff twin",
        "Payment retries use exponential backoff and cap at five attempts.",
        "policy:retry",
    )
    stele.link(a, kind="entry", ref=b, actor="ops", ts=TS)

    d = stele.result_digest({"count": 2, "ids": [a, b]})
    assert len(d["digest"]) == 64

    assert stele.operator_cost_estimate(
        [{"op": "as_of_belief", "limit": 5}], max_cost=40
    )["admitted"]

    assert stele.plan_static_verify(
        {
            "steps": [
                {
                    "id": "s0",
                    "op": "resolve_entities",
                    "literal_ids": [a],
                    "outputs": ["count", "digest"],
                },
                {
                    "id": "s1",
                    "op": "compute_count",
                    "refs": ["s0"],
                    "outputs": ["count", "digest"],
                },
            ],
            "answer": {"step": "s1", "field": "count"},
        },
        task_ids=[a],
    )["valid"]

    assert not stele.plan_static_verify(
        {
            "steps": [
                {
                    "id": "s0",
                    "op": "compute_count",
                    "literal_ids": ["ghost"],
                    "outputs": ["count"],
                }
            ],
            "answer": {"step": "s0", "field": "count"},
        },
        task_ids=[a],
    )["valid"]

    trace = {
        "steps": {
            "s1": {
                "fields": {"count": 2, "entities": [a], "order": [a, b]},
                "truncated": False,
            }
        }
    }
    assert stele.claim_verify(
        [{"kind": "count", "cite": "s1", "expect": 2}],
        trace,
    )["ok"]
    assert stele.claim_verify(
        [{"kind": "count", "cite": "s1", "expect": 9}],
        trace,
    )["blocked"]

    q = stele.summary_quarantine_scan(
        [{"id": "n1", "valid_from": "2026-08-01T00:00:00Z", "valid_to": "2026-09-01T00:00:00Z"}],
        [{"id": "c1", "valid_from": "2026-08-10T00:00:00Z", "valid_to": "2026-08-12T00:00:00Z"}],
    )
    assert q["count"] == 1

    local = stele.localized_maintenance_plan([a], radius=1)
    assert local["global_reorganize"] is False
    assert a in local["touch_ids"]
    assert b in local["touch_ids"]
    assert stele.maintenance_cost_compare(local["touch_count"])["prefer_local"]


def test_harness_v44(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "h", store_id="h", now=TS)
    report = tgms_memdata_shaped_report(
        stele, consumer_scope="project:demo", now=TS
    )
    assert report["suite"] == "tgms_memdata_shaped"
    assert report["ok"] is True
