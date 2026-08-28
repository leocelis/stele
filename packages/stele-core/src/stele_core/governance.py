"""Quarantine → promote governance and evidence checks (C7)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError, validate_evidence
from stele_core.store import SteleStore


def validate_promotion_evidence(
    entry: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
    *,
    store: SteleStore | None = None,
    require_test_result_for_code_fix: bool = False,
) -> list[dict[str, Any]]:
    """Validate evidence for promotion. Self-grades are structurally rejected."""
    if not evidence:
        raise SchemaError("promotion requires at least one evidence record")

    writer = str(entry["provenance"]["agent"])
    validated: list[dict[str, Any]] = []
    for rec in evidence:
        v = validate_evidence(rec, writer_agent=writer)
        digest = v.get("digest")
        if digest and store is not None:
            att = store.attachments / digest
            if att.exists() and not store.verify_attachment_digest(digest):
                raise SchemaError(f"evidence digest mismatch for {digest}")
        validated.append(v)

    proj = entry.get("receipt_projection") or {}
    need_test = require_test_result_for_code_fix or bool(proj.get("code_regression"))
    if need_test:
        ok = any(
            e["type"] == "test_result" and e.get("exit_status") == 0 for e in validated
        )
        if not ok:
            raise SchemaError(
                "code-fix lessons require test_result evidence with exit_status=0"
            )

    return validated


def apply_promote(
    store: SteleStore,
    entry_id: str,
    evidence: Sequence[Mapping[str, Any]],
    *,
    actor: str,
    ts: str,
    require_test_result_for_code_fix: bool = False,
) -> dict[str, Any]:
    entry = store.read_entry(entry_id)
    if entry is None:
        raise SchemaError(f"unknown entry: {entry_id}")
    if entry["state"] != "quarantined":
        raise SchemaError(f"only quarantined entries can promote, got {entry['state']}")

    # C8 retrieval_roles.writer: Can ADD only; cannot promote its own claim.
    writer = str(entry["provenance"]["agent"])
    if actor == writer:
        raise SchemaError(
            "writer cannot promote its own claim; a separate oracle actor is required"
        )

    validated = validate_promotion_evidence(
        entry,
        evidence,
        store=store,
        require_test_result_for_code_fix=require_test_result_for_code_fix,
    )
    entry["evidence"] = validated
    entry["state"] = "promoted"
    entry["temporal"]["last_verified"] = ts
    return store.write_entry(entry, actor=actor, ts=ts, op="PROMOTE")


def apply_resolve_contested(
    store: SteleStore,
    *,
    winner_id: str,
    loser_id: str,
    evidence: Sequence[Mapping[str, Any]],
    actor: str,
    ts: str,
) -> dict[str, Any]:
    """
    Resolve a REFLECT conflict by evidenced supersede (TECH_SPEC Q5 / R2).

    No auto-merge: an external actor chooses the winner and attaches oracle evidence.
    Winner → promoted (evidence appended). Loser → superseded.
    """
    if winner_id == loser_id:
        raise SchemaError("winner_id and loser_id must differ")

    winner = store.read_entry(winner_id)
    loser = store.read_entry(loser_id)
    if winner is None or loser is None:
        raise SchemaError("both winner and loser must exist")
    if winner["state"] != "contested" or loser["state"] != "contested":
        raise SchemaError("both entries must be in contested state to resolve")

    peers_w = set(winner.get("contested_with") or [])
    peers_l = set(loser.get("contested_with") or [])
    if loser_id not in peers_w and winner_id not in peers_l:
        # Allow resolve if they share scope + were conflict-flagged without peer links
        if winner["scope"] != loser["scope"]:
            raise SchemaError("contested pair must share scope or contested_with links")

    if actor == winner["provenance"]["agent"] or actor == loser["provenance"]["agent"]:
        raise SchemaError(
            "conflict authors cannot resolve their own contested pair; "
            "use a separate oracle actor"
        )

    validated = validate_promotion_evidence(winner, evidence, store=store)
    # Prefer supporting evidence for the winner
    if not any(v.get("verdict") == "supports" for v in validated):
        raise SchemaError("resolve requires at least one evidence record with verdict=supports")

    winner = dict(winner)
    winner["evidence"] = list(winner.get("evidence") or []) + validated
    winner["state"] = "promoted"
    winner["temporal"] = dict(winner["temporal"])
    winner["temporal"]["last_verified"] = ts
    winner["contested_with"] = [
        p for p in (winner.get("contested_with") or []) if p != loser_id
    ]
    store.write_entry(winner, actor=actor, ts=ts, op="RESOLVE_WIN")

    loser = dict(loser)
    loser["state"] = "superseded"
    loser["temporal"] = dict(loser["temporal"])
    loser["temporal"]["superseded_by"] = winner_id
    loser["temporal"]["superseded_at"] = ts
    loser["contested_with"] = [
        p for p in (loser.get("contested_with") or []) if p != winner_id
    ]
    store.write_entry(loser, actor=actor, ts=ts, op="RESOLVE_LOSE")

    return {
        "winner_id": winner_id,
        "loser_id": loser_id,
        "winner_state": "promoted",
        "loser_state": "superseded",
    }
