"""C8 — receipt adapter projection preserves structure and redacts private sources."""

from __future__ import annotations

import pytest

from stele_core import SchemaError, Stele, project_receipt
from helpers import TS, oracle_evidence


def test_projection_preserves_structure_and_redacts_private_source(stele: Stele) -> None:
    with pytest.raises(SchemaError, match="private-source"):
        project_receipt(
            {
                "diagnosis": "cache bug",
                "detection": "stale reads",
                "source": "workspace/ledger/tenants/private/feedback/x.yaml",
                "subject_id": "s1",
            },
            written_at=TS,
        )

    receipt = {
        "expected": "stable cache",
        "detection": "stale reads after midnight",
        "diagnosis": "key lacked day bucket",
        "change_tried": "pin key to calendar day",
        "outcome": "fixed",
        "code_regression": True,
        "agent": "receipt-writer",
        "task": "cache",
        "environment": "ci",
        "subject_id": "subj-r",
        "source": "receipt:redacted",
        "scope": "project:demo",
        "domain_depth": "practitioner",
        "model_id": "test-model",
        "links": [{"kind": "test", "ref": "tests/test_cache.py"}],
    }
    payload = project_receipt(receipt, written_at=TS)
    assert payload["layer"] == "failure_lesson"
    assert payload["receipt_projection"]["detection"] != payload["receipt_projection"]["diagnosis"]
    assert payload["receipt_projection"]["code_regression"] is True
    assert payload["provenance"]["model_id"] == "test-model"
    assert payload["assessment"]["domain_depth"] == "practitioner"

    eid = stele.add(payload, ts=TS)["id"]

    # Code-regression promote without test_result must fail
    with pytest.raises(SchemaError, match="test_result"):
        stele.promote(
            eid,
            [
                {
                    "type": "human_signoff",
                    "issuer": "leo",
                    "ref": "lgtm",
                    "observed_at": TS,
                    "verdict": "supports",
                }
            ],
            actor="leo",
            ts=TS,
            require_test_result_for_code_fix=True,
        )

    stele.promote(
        eid,
        oracle_evidence(issuer="ci"),
        actor="ci",
        ts=TS,
        require_test_result_for_code_fix=True,
    )
    hits = stele.search("day bucket", consumer_scope="project:demo")
    assert len(hits) == 1
