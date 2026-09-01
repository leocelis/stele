"""LoRETTA proxies (stdlib; no LLM).

Shaped by LoRETTA (arXiv:2402.11417): tensor-train adapters (adp)
or TT reparam of weights (rep). Proxies only.

Prefix ``ltt_*`` — not LoRTA (``lrt_*``) / LoTR (``ltr_*``) /
CaRA (``cra_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def ltt_adp(*, task: str) -> dict[str, Any]:
    """Open the tensorized-adapter (adp) branch."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    aid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "adp_id": aid,
        "ok": True,
        "note": "ltt ltt_adp",
    }


def ltt_rep(*, adp_id: str) -> dict[str, Any]:
    """Open the TT reparam (rep) branch."""
    aid = adp_id.strip()
    if not aid:
        raise SchemaError("adp_id required")
    rid = hashlib.sha256(
        canonical_dumps({"a": aid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "rep_id": rid,
        "ok": True,
        "note": "ltt ltt_rep",
    }


def ltt_tt(*, rep_id: str) -> dict[str, Any]:
    """Apply tensor-train cores."""
    rid = rep_id.strip()
    if not rid:
        raise SchemaError("rep_id required")
    tid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "tt_id": tid,
        "ok": True,
        "note": "ltt ltt_tt",
    }


def ltt_score(*, tt_id: str, score: int) -> dict[str, Any]:
    """Score LoRETTA run (0–100)."""
    tid = tt_id.strip()
    if not tid:
        raise SchemaError("tt_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"t": tid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "ltt ltt_score",
    }


def ltt_tiny(*, sub_mb: bool) -> dict[str, Any]:
    """Flag <1MB rep storage (report-only)."""
    return {
        "sub_mb": sub_mb,
        "apply": False,
        "ok": True,
        "note": "ltt ltt_tiny",
    }


def ltt_loop_plan(*, phase: str) -> dict[str, Any]:
    """Adp → rep → tt → score."""
    order = ("adp", "rep", "tt", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "adp"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "ltt ltt_loop_plan",
    }
