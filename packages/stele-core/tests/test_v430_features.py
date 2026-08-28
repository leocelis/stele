"""v4.3: SodaMem density/cite + MemRefine + AriadneMem/MemFuse."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, sodamem_memrefine_ariadne_shaped_report

TS = "2026-08-21T12:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v43",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def _promote(stele: Stele, title: str, body: str, ck: str, helpful: int = 1) -> str:
    eid = stele.add(
        {
            "layer": "decision",
            "title": title,
            "body": body,
            "scope": "project:v43",
            "conflict_key": ck,
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "oracle",
                "task": "v43",
                "environment": "local",
                "subject_id": "s",
                "source": "oracle:v43",
                "written_at": TS,
            },
            "usage": {"helpful": helpful, "harmful": 0, "pinned": False},
        },
        ts=TS,
    )["id"]
    stele.promote(eid, EV, actor="ci", ts=TS)
    return eid


def test_sodamem_memrefine_ariadne(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v43", now=TS)
    a = _promote(
        stele,
        "Retry backoff",
        "Payment retries use exponential backoff and cap at five.",
        "policy:retry",
        helpful=3,
    )
    b = _promote(
        stele,
        "Retry backoff copy",
        "Payment retries use exponential backoff and cap at five attempts.",
        "policy:retry",
        helpful=1,
    )
    c = _promote(
        stele,
        "Timeout policy",
        "HTTP client timeout is thirty seconds for payment calls.",
        "policy:timeout",
    )
    stele.link(a, kind="entry", ref=b, actor="ops", ts=TS)
    stele.link(b, kind="entry", ref=c, actor="ops", ts=TS)

    fuse = stele.density_fuse(
        [
            {
                "id": a,
                "tunnel": "lexical",
                "strength": "strong",
                "kind": "direct",
                "score": 1.0,
            },
            {
                "id": a,
                "tunnel": "link",
                "strength": "weak",
                "kind": "derived",
                "score": 0.5,
            },
        ]
    )
    assert fuse["fused"][0]["id"] == a
    assert fuse["fused"][0]["mass"] > 0.4

    plan = stele.evidence_plan("payment retries backoff")
    assert plan["count"] >= 1
    ids = [e["id"] for e in plan["evidence"]]
    pack = stele.cited_pack("payment retries backoff", ids)
    assert pack["all_cited"] is True
    assert all(b.get("citation") for b in pack["blocks"])

    cand = stele.compress_candidates(min_similarity=0.4)
    assert cand["count"] >= 1
    refine = stele.refine_plan(target_count=2, min_similarity=0.4)
    assert refine["ok"] is True
    assert refine["final_count"] <= 2
    assert refine["action_count"] >= 1

    mla = stele.merge_link_add(
        {
            "title": "Retry backoff again",
            "body": "Payment retries use exponential backoff and cap at five.",
            "scope": "project:v43",
            "conflict_key": "policy:retry",
        }
    )
    assert mla["decision"] in {"merge", "link"}

    br = stele.bridge_discover([a, c])
    assert br["found_count"] >= 1
    assert br["bridges"][0]["path"][0] == a

    cl = stele.fuse_cluster([a, b, c], label="payment")
    assert cl["member_count"] == 3
    assert cl["ok"] is True


def test_harness_v43(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "h", store_id="h", now=TS)
    report = sodamem_memrefine_ariadne_shaped_report(
        stele, consumer_scope="project:demo", now=TS
    )
    assert report["suite"] == "sodamem_memrefine_ariadne_shaped"
    assert report["ok"] is True
