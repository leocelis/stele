"""C2 — promoted-only retrieval with scope/validity filters."""

from __future__ import annotations

from stele_core import Stele
from helpers import TS, base_entry, oracle_evidence


def test_quarantine_never_served_and_filters_applied(stele: Stele) -> None:
    q = stele.add(base_entry(title="Quarantined cache tip"), ts=TS)["id"]

    other = stele.add(
        base_entry(
            title="Other project lesson about cache",
            body="Scoped elsewhere.",
            scope="project:other",
            provenance={
                "agent": "agent-b",
                "task": "x",
                "environment": "local",
                "subject_id": "subj-other",
                "source": "session:o",
                "written_at": TS,
            },
        ),
        ts=TS,
    )["id"]
    stele.promote(other, oracle_evidence(issuer="oracle-b"), actor="oracle-b", ts=TS)

    expired = stele.add(
        base_entry(
            title="Expired cache guidance",
            body="Old advice about cache keys.",
            temporal={
                "valid_from": "2026-01-01T00:00:00Z",
                "last_verified": "2026-01-01T00:00:00Z",
                "expiry": "2026-02-01T00:00:00Z",
            },
            provenance={
                "agent": "agent-c",
                "task": "y",
                "environment": "local",
                "subject_id": "subj-exp",
                "source": "session:e",
                "written_at": "2026-01-01T00:00:00Z",
            },
        ),
        ts=TS,
    )["id"]
    stele.promote(expired, oracle_evidence(issuer="oracle-c"), actor="oracle-c", ts=TS)
    stele.reflect(actor="maint", ts=TS)  # expiry <= now → expired

    good = stele.add(
        base_entry(
            title="Valid promoted cache bucket lesson",
            body="Pin cache keys to calendar day buckets.",
        ),
        ts=TS,
    )["id"]
    stele.promote(good, oracle_evidence(), actor="ci-oracle", ts=TS)

    hits = stele.search("cache bucket", consumer_scope="project:demo", budget=400)
    ids = [h["id"] for h in hits]
    assert q not in ids
    assert other not in ids
    assert expired not in ids
    assert ids == [good]
