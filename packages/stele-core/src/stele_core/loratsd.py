"""LoRA-TSD proxies (stdlib; no LLM).

Shaped by LoRA-TSD (arXiv:2409.01035): combine LoRA-Init TSD
initialization with LoRA-Dash TSD amplification into one TSD-based
adaptation loop. Proxies only.

Prefix ``lts_*`` — not LoRA-Dash (``lds_*``) / LoRA-Init (``lin_*``) /
S-LoRA (``slr_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lts_tsd(*, task: str, count: int) -> dict[str, Any]:
    """Identify task-specific directions (count >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if count < 1:
        raise SchemaError("count must be >= 1")
    tid = hashlib.sha256(
        canonical_dumps({"t": t, "c": count}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "tsd_id": tid,
        "count": count,
        "ok": True,
        "note": "lts lts_tsd",
    }


def lts_init(*, tsd_id: str) -> dict[str, Any]:
    """Initialize LoRA from identified TSDs (LoRA-Init half)."""
    tid = tsd_id.strip()
    if not tid:
        raise SchemaError("tsd_id required")
    iid = hashlib.sha256(
        canonical_dumps({"t": tid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "init_id": iid,
        "ok": True,
        "note": "lts lts_init",
    }


def lts_dash(*, init_id: str) -> dict[str, Any]:
    """Amplify TSDs during training (LoRA-Dash half)."""
    iid = init_id.strip()
    if not iid:
        raise SchemaError("init_id required")
    did = hashlib.sha256(
        canonical_dumps({"i": iid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "dash_id": did,
        "ok": True,
        "note": "lts lts_dash",
    }


def lts_score(*, dash_id: str, score: int) -> dict[str, Any]:
    """Score LoRA-TSD adaptation (0–100)."""
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
        "note": "lts lts_score",
    }


def lts_combo(*, uses_both: bool) -> dict[str, Any]:
    """Flag Init+Dash combined TSD loop (report-only)."""
    return {
        "uses_both": uses_both,
        "apply": False,
        "ok": True,
        "note": "lts lts_combo",
    }


def lts_loop_plan(*, phase: str) -> dict[str, Any]:
    """TSD → init → dash → score."""
    order = ("tsd", "init", "dash", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "tsd"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lts lts_loop_plan",
    }
