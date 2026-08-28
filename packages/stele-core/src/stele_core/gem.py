"""GEM-shaped state-operator correctness checklist (stdlib)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def gem_correctness_report(capabilities: Mapping[str, bool]) -> dict[str, Any]:
    """
    Governed Evolving Memory (GEM) six-condition coverage checklist.

    Local obligation presence — not MemState engine claims (arXiv:2605.26252).
    """
    conditions = [
        ("C1_query_soundness", "exclude_superseded_or_winners"),
        ("C2_transition_soundness", "verify_transition_or_tarl"),
        ("C3_ingestion_gated", "quarantine_promote"),
        ("C4_revision_explicit", "supersede_or_revoke"),
        ("C5_forgetting", "delete_or_forget_compliance"),
        ("C6_retrieval_governed", "scope_acl_or_action_safe"),
    ]
    rows = []
    for code, key in conditions:
        rows.append(
            {
                "condition": code,
                "capability_key": key,
                "present": bool(capabilities.get(key)),
            }
        )
    score = sum(1 for r in rows if r["present"]) / len(rows)
    return {
        "framework": "GEM-shaped",
        "score": round(score, 4),
        "conditions": rows,
        "ok": score >= 1.0,
        "note": "state-trajectory correctness obligations — not a native GEM engine",
    }
