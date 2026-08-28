"""C7 — quarantine promotion requires external oracle; self-grade never promotes."""

from __future__ import annotations

import pytest

from stele_core import SchemaError, Stele
from helpers import TS, base_entry, oracle_evidence


def test_self_graded_never_promotes(stele: Stele) -> None:
    eid = stele.add(base_entry(), ts=TS)["id"]

    # Separate oracle actor, but evidence issuer == writer → still blocked (C7)
    with pytest.raises(SchemaError, match="self-issued"):
        stele.promote(
            eid,
            [
                {
                    "type": "env_feedback",
                    "issuer": "agent-a",  # same as provenance.agent
                    "ref": "I think it worked",
                    "observed_at": TS,
                    "verdict": "supports",
                }
            ],
            actor="ci-oracle",
            ts=TS,
        )

    # Still quarantined — not searchable
    assert stele.search("cache", consumer_scope="project:demo") == []

    stele.promote(eid, oracle_evidence(), actor="ci-oracle", ts=TS)
    hits = stele.search("cache buckets", consumer_scope="project:demo")
    assert len(hits) == 1
    assert hits[0]["id"] == eid
    assert hits[0]["stale"] is False
