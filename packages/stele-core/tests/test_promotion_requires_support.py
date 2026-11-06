"""Search only admits a lesson whose evidence says it holds (C7, UC-13).

Before this rule, a lesson whose only evidence refuted it, or whose test exited 1,
was promoted and returned by search: the gate checked who signed the evidence and
never read what the evidence said.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from helpers import TS, base_entry, oracle_evidence
from stele_core import SchemaError, Stele


def _record(verdict: str, **extra: Any) -> dict[str, Any]:
    return {
        "type": "env_feedback",
        "issuer": "ci",
        "ref": "prod-log",
        "observed_at": TS,
        "verdict": verdict,
        **extra,
    }


def _test_result(verdict: str, exit_status: int) -> dict[str, Any]:
    return _record(
        verdict, type="test_result", command="pytest -q", exit_status=exit_status
    )


BAD_EVIDENCE = {
    "only_refutes": [_record("refutes")],
    "only_mixed": [_record("mixed")],
    "supports_and_refutes": [_record("supports"), _record("refutes")],
    "failing_test_labelled_supports": [_test_result("supports", 1)],
    "failing_test_refutes": [_test_result("refutes", 1)],
}


@pytest.fixture
def stele(tmp_path: Path) -> Stele:
    return Stele.open(tmp_path / "s", store_id="support", now=TS)


@pytest.mark.parametrize("case", sorted(BAD_EVIDENCE))
def test_unsupported_lesson_stays_out_of_search(stele: Stele, case: str) -> None:
    eid = stele.add(base_entry(), ts=TS)["id"]
    with pytest.raises(SchemaError):
        stele.promote(eid, BAD_EVIDENCE[case], actor="ci", ts=TS)
    assert stele.store.read_entry(eid)["state"] == "quarantined"
    assert stele.search("cache", consumer_scope="project:demo") == []


@pytest.mark.parametrize(
    "evidence",
    [
        [_record("supports")],
        [_test_result("supports", 0)],
        [_record("supports"), _record("mixed")],
    ],
    ids=["feedback", "passing_test", "supports_with_mixed"],
)
def test_supported_lesson_promotes(stele: Stele, evidence: list[dict[str, Any]]) -> None:
    eid = stele.add(base_entry(), ts=TS)["id"]
    assert stele.promote(eid, evidence, actor="ci", ts=TS)["state"] == "promoted"


def test_unrevoke_needs_the_same_evidence_as_promotion(stele: Stele) -> None:
    eid = stele.add(base_entry(conflict_key="deploy.cache"), ts=TS)["id"]
    stele.promote(eid, oracle_evidence(), actor="ci", ts=TS)
    stele.revoke_by_key("deploy.cache", evidence=[_record("supports")], actor="ops", ts=TS)
    with pytest.raises(SchemaError):
        stele.unrevoke(eid, evidence=[_record("refutes")], actor="ops", ts=TS)
    assert stele.store.read_entry(eid)["state"] == "revoked"
    writer = stele.store.read_entry(eid)["provenance"]["agent"]
    with pytest.raises(SchemaError, match="self-issued"):
        stele.unrevoke(
            eid, evidence=[_record("supports", issuer=writer)], actor="ops", ts=TS
        )
    assert stele.unrevoke(eid, evidence=[_record("supports")], actor="ops", ts=TS)[
        "state"
    ] == "promoted"


def test_later_refuting_evidence_still_reaches_a_promoted_lesson(stele: Stele) -> None:
    """The rule must not close the only route to a contested pair."""
    eid = stele.add(base_entry(), ts=TS)["id"]
    stele.promote(eid, oracle_evidence(), actor="ci", ts=TS)
    stele.reverify([eid], [_record("refutes")], actor="ci", ts=TS)
    verdicts = {e["verdict"] for e in stele.store.read_entry(eid)["evidence"]}
    assert verdicts == {"supports", "refutes"}
