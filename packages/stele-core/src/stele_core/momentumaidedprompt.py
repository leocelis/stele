"""MAPO proxies (stdlib; no LLM).

Shaped by MAPO (arXiv:2410.19499): positive textual gradients + momentum
memory over ProTeGi-style beam/UCB selection. Proxies only.

Prefix ``mapo_*`` — not ProTeGi (``ptg_*``) / GrIPS (``grips_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def mapo_posgrad(*, prompt: str) -> dict[str, Any]:
    """Form positive natural-language gradients from correct minibatch examples."""
    p = prompt.strip()
    if not p:
        raise SchemaError("prompt required")
    gid = hashlib.sha256(
        canonical_dumps({"p": p}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "pos_id": gid,
        "ok": True,
        "note": "mapo mapo_posgrad",
    }


def mapo_momentum(*, pos_id: str) -> dict[str, Any]:
    """Apply momentum memory over gradient history (anti-oscillation)."""
    pid = pos_id.strip()
    if not pid:
        raise SchemaError("pos_id required")
    mid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "mom_id": mid,
        "ok": True,
        "note": "mapo mapo_momentum",
    }


def mapo_beam(*, mom_id: str) -> dict[str, Any]:
    """Expand child prompt candidates via beam search."""
    mid = mom_id.strip()
    if not mid:
        raise SchemaError("mom_id required")
    bid = hashlib.sha256(
        canonical_dumps({"m": mid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "beam_id": bid,
        "ok": True,
        "note": "mapo mapo_beam",
    }


def mapo_ucb(*, beam_id: str, score: int) -> dict[str, Any]:
    """UCB bandit selection over beam candidates (score 0–100)."""
    bid = beam_id.strip()
    if not bid:
        raise SchemaError("beam_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    uid = hashlib.sha256(
        canonical_dumps({"b": bid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "ucb_id": uid,
        "score": score,
        "ok": True,
        "note": "mapo mapo_ucb",
    }


def mapo_faster(*, beat_protegi: bool) -> dict[str, Any]:
    """Flag faster convergence vs ProTeGi (report-only)."""
    return {
        "beat_protegi": beat_protegi,
        "apply": False,
        "ok": True,
        "note": "mapo mapo_faster",
    }


def mapo_loop_plan(*, phase: str) -> dict[str, Any]:
    """Posgrad → momentum → beam → ucb."""
    order = ("posgrad", "momentum", "beam", "ucb")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "posgrad"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "mapo mapo_loop_plan",
    }
