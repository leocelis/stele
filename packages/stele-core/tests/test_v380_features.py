"""v3.8: ProGraph residuals/expand + EMG correction + AgentIR cascade."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, prograph_emg_agentir_shaped_report

TS = "2026-08-21T00:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v38",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def test_prograph_emg_agentir(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v38", now=TS)
    fail = stele.add(
        {
            "layer": "failure_lesson",
            "title": "Webhook retry storm",
            "body": "Payment webhook retries without backoff flooded the queue on 2026-08-01.",
            "scope": "project:v38",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "oracle",
                "task": "fail",
                "environment": "local",
                "subject_id": "s",
                "source": "oracle:gate",
                "written_at": TS,
            },
            "usage": {"helpful": 1, "harmful": 0},
        },
        ts=TS,
    )["id"]
    stele.promote(fail, EV, actor="ci", ts=TS)
    ok = stele.add(
        {
            "layer": "workflow",
            "title": "Webhook backoff workflow",
            "body": (
                "Payment webhook retries use exponential backoff and cap at five. "
                "Record latency after each attempt."
            ),
            "scope": "project:v38",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "oracle",
                "task": "ok",
                "environment": "local",
                "subject_id": "s",
                "source": "oracle:gate",
                "written_at": TS,
            },
            "usage": {"helpful": 3, "harmful": 0, "pinned": True},
            "env_assumptions": ["local", "pytest"],
        },
        ts=TS,
    )["id"]
    stele.promote(ok, EV, actor="ci", ts=TS)

    res = stele.extract_residuals(fail)
    assert res["count"] >= 1
    assert any(r["kind"] == "date" for r in res["residuals"])

    ents = stele.register_entities()
    assert ents["count"] >= 1

    expand = stele.profile_expand("payment webhook backoff")
    assert expand["ok"] is True
    assert expand["seed_count"] >= 1

    aug = stele.residual_augment("2026-08-01 payment", [fail])
    assert aug["ok"] is True
    assert aug["count"] == 1

    match = stele.match_correction(failure_id=fail, min_overlap=0.05)
    assert match["ok"] is True
    pair = match["pairs"][0]
    assert pair["success_id"] == ok
    assert pair["action"] == "apply_edit_path"

    insight = stele.insight_inject(pair)
    assert insight["ok"] is True
    assert "Prefer" in insight["insight"]

    route = stele.cascade_route(
        "payment webhook backoff", consumer_scope="project:v38"
    )
    assert route["mode"] in {"lexical_only", "full_rrf"}

    fuse = stele.multi_channel_fuse(
        "payment webhook backoff",
        consumer_scope="project:v38",
        force_full=True,
    )
    assert fuse["ok"] is True
    assert fuse["count"] >= 1
    assert "lexical" in fuse["channels"]


def test_harness_v38(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "h", store_id="h", now=TS)
    report = prograph_emg_agentir_shaped_report(
        stele, consumer_scope="project:demo", now=TS
    )
    assert report["suite"] == "prograph_emg_agentir_shaped"
    assert report["ok"] is True
