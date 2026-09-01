"""v4.1: BudgetMem tiers + skill library ranker + ERSkill retrieval skills."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, budgetmem_erskill_shaped_report

TS = "2026-08-21T00:00:00Z"
EV = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "v41",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def test_budgetmem_erskill(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v41", now=TS)
    skill = stele.add(
        {
            "layer": "skill_artifact",
            "title": "Payment backoff skill",
            "body": "Procedure: apply exponential backoff then cap payment retries at five.",
            "scope": "project:v41",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "oracle",
                "task": "skill",
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
    stele.promote(skill, EV, actor="ci", ts=TS)
    dep = stele.add(
        {
            "layer": "workflow",
            "title": "Webhook observe workflow",
            "body": "Log payment webhook latency before applying backoff skill.",
            "scope": "project:v41",
            "temporal": {"valid_from": TS, "last_verified": TS},
            "provenance": {
                "agent": "oracle",
                "task": "dep",
                "environment": "local",
                "subject_id": "s",
                "source": "oracle:gate",
                "written_at": TS,
            },
            "usage": {"helpful": 2, "harmful": 0},
            "env_assumptions": ["local", "pytest"],
            "links": [{"kind": "entry", "ref": skill}],
        },
        ts=TS,
    )["id"]
    stele.promote(dep, EV, actor="ci", ts=TS)

    assert stele.query_complexity("why compare every hop")["band"] in {
        "mid",
        "high",
    }
    assert stele.budget_tier_route("payment")["ok"] is True
    plan = stele.budget_module_plan(
        "why compare every payment hop history", global_budget=6
    )
    assert plan["fits"] is True
    assert plan["estimated_cost"] <= 6

    rank = stele.skill_rank("payment backoff skill")
    assert any(h["id"] == skill for h in rank["hits"])
    assert skill in stele.skill_prereq_expand(dep)["reachable_ids"]

    assert stele.list_retrieval_primitives()["count"] >= 5
    assert stele.list_retrieval_skills()["count"] >= 3
    assert stele.compose_retrieval_skill(
        "x", ["lexical_search", "multi_hop"]
    )["ok"]
    assert stele.route_retrieval_skill("current latest version")["skill"] == "current_facts"

    run = stele.run_retrieval_skill(
        "payment backoff",
        consumer_scope="project:v41",
        skill="skill_first",
    )
    assert run["ok"] is True
    assert run["skill"] == "skill_first"


def test_harness_v41(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "h", store_id="h", now=TS)
    report = budgetmem_erskill_shaped_report(
        stele, consumer_scope="project:demo", now=TS
    )
    assert report["suite"] == "budgetmem_erskill_shaped"
    assert report["ok"] is True
