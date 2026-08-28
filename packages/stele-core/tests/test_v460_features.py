"""v4.6: MemForest MemTree + xMemory top-down themes."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, memforest_xmemory_shaped_report

TS = "2026-08-22T12:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v46",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def _promote(
    stele: Stele, title: str, body: str, ck: str, day: str
) -> str:
    eid = stele.add(
        {
            "layer": "decision",
            "title": title,
            "body": body,
            "scope": "project:v46",
            "conflict_key": ck,
            "temporal": {
                "valid_from": f"{day}T00:00:00Z",
                "last_verified": f"{day}T00:00:00Z",
            },
            "provenance": {
                "agent": "oracle",
                "task": "v46",
                "environment": "local",
                "subject_id": "s",
                "source": "oracle:v46",
                "written_at": f"{day}T00:00:00Z",
            },
        },
        ts=f"{day}T00:00:00Z",
    )["id"]
    stele.promote(eid, EV, actor="ci", ts=f"{day}T00:00:00Z")
    return eid


def test_memforest_xmemory(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v46", now=TS)
    _promote(
        stele,
        "Retry backoff",
        "Payment retries use exponential backoff and cap at five.",
        "policy:retry",
        "2026-08-01",
    )
    _promote(
        stele,
        "Timeout policy",
        "HTTP client timeout is thirty seconds for payment calls.",
        "policy:timeout",
        "2026-08-02",
    )
    _promote(
        stele,
        "Retry note two",
        "Payment retries backoff tip for production.",
        "policy:retry",
        "2026-08-01",
    )

    tree = stele.build_memtree(scope="project:v46")
    assert tree["root"]["leaf_count"] == 3
    assert tree["root"]["interval_count"] == 2

    dirty = stele.dirty_path_plan(
        {
            "id": "x",
            "title": "n",
            "body": "b",
            "temporal": {"valid_from": "2026-08-01T12:00:00Z"},
        },
        scope="project:v46",
    )
    assert dirty["global_rewrite"] is False
    assert "interval:2026-08-01" in dirty["dirty_path"]

    ctf = stele.coarse_to_fine("payment retries backoff", scope="project:v46")
    assert ctf["count"] >= 1

    themes = stele.build_themes(scope="project:v46")
    assert themes["count"] >= 2

    attach = stele.theme_attach(
        {
            "title": "Retry again",
            "body": "Payment retries use exponential backoff.",
        },
        scope="project:v46",
    )
    assert attach["decision"] in {"attach", "create_theme"}

    sm = stele.split_merge_plan(scope="project:v46", max_size=1)
    assert any(a["action"] == "split" for a in sm["actions"])

    pack = stele.top_down_pack("payment retries", scope="project:v46")
    assert pack["ok"] is True
    assert pack["used"] <= pack["budget"]


def test_harness_v46(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "h", store_id="h", now=TS)
    report = memforest_xmemory_shaped_report(
        stele, consumer_scope="project:demo", now=TS
    )
    assert report["suite"] == "memforest_xmemory_shaped"
    assert report["ok"] is True
