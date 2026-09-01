"""LoRA-Dash proxies (stdlib; no LLM).

Shaped by LoRA-Dash (arXiv:2409.01035): identify task-specific directions
(TSDs) in a pre-launch phase, then amplify them in a dash phase.
Proxies only.

Prefix ``lds_*`` — not LoftQ (``lfq_*``) / LoRA-Pro (``lpr_*``) / LoRA-XS.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lds_prelaunch(*, task: str) -> dict[str, Any]:
    """Declare pre-launch phase to detect task-specific directions."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    pid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "prelaunch_id": pid,
        "ok": True,
        "note": "lds lds_prelaunch",
    }


def lds_tsd(*, prelaunch_id: str, count: int) -> dict[str, Any]:
    """Select top task-specific directions (count >= 1)."""
    pid = prelaunch_id.strip()
    if not pid:
        raise SchemaError("prelaunch_id required")
    if count < 1:
        raise SchemaError("count must be >= 1")
    tid = hashlib.sha256(
        canonical_dumps({"p": pid, "c": count}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "tsd_id": tid,
        "count": count,
        "ok": True,
        "note": "lds lds_tsd",
    }


def lds_dash(*, tsd_id: str) -> dict[str, Any]:
    """Dash phase — amplify identified TSDs."""
    tid = tsd_id.strip()
    if not tid:
        raise SchemaError("tsd_id required")
    did = hashlib.sha256(
        canonical_dumps({"t": tid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "dash_id": did,
        "ok": True,
        "note": "lds lds_dash",
    }


def lds_score(*, dash_id: str, score: int) -> dict[str, Any]:
    """Score LoRA-Dash adaptation (0–100)."""
    did = dash_id.strip()
    if not did:
        raise SchemaError("dash_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"d": did, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "lds lds_score",
    }


def lds_impact(*, maximizes_tsd: bool) -> dict[str, Any]:
    """Flag TSD impact maximized (report-only)."""
    return {
        "maximizes_tsd": maximizes_tsd,
        "apply": False,
        "ok": True,
        "note": "lds lds_impact",
    }


def lds_loop_plan(*, phase: str) -> dict[str, Any]:
    """Prelaunch → tsd → dash → score."""
    order = ("prelaunch", "tsd", "dash", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "prelaunch"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lds lds_loop_plan",
    }
