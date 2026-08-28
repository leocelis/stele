"""ProTeGi proxies (stdlib; no LLM).

Shaped by ProTeGi (arXiv:2305.03495): textual gradients criticize the
current prompt; edits move opposite the gradient; beam + bandit select.
Proxies only.

Prefix ``ptg_*`` — not OPRO (``opro_*``) / PromptAgent (``pag_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def ptg_gradient(*, prompt: str) -> dict[str, Any]:
    """Form a natural-language textual gradient from minibatch errors."""
    p = prompt.strip()
    if not p:
        raise SchemaError("prompt required")
    gid = hashlib.sha256(
        canonical_dumps({"p": p}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "grad_id": gid,
        "ok": True,
        "note": "ptg ptg_gradient",
    }


def ptg_edit(*, grad_id: str) -> dict[str, Any]:
    """Propagate gradient: edit prompt opposite the semantic gradient."""
    gid = grad_id.strip()
    if not gid:
        raise SchemaError("grad_id required")
    eid = hashlib.sha256(
        canonical_dumps({"g": gid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "edit_id": eid,
        "ok": True,
        "note": "ptg ptg_edit",
    }


def ptg_beam(*, edit_id: str) -> dict[str, Any]:
    """Expand edited candidates via beam search."""
    eid = edit_id.strip()
    if not eid:
        raise SchemaError("edit_id required")
    bid = hashlib.sha256(
        canonical_dumps({"e": eid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "beam_id": bid,
        "ok": True,
        "note": "ptg ptg_beam",
    }


def ptg_bandit(*, beam_id: str, score: int) -> dict[str, Any]:
    """Best-arm / bandit selection over beam candidates (score 0–100)."""
    bid = beam_id.strip()
    if not bid:
        raise SchemaError("beam_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"b": bid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "arm_id": sid,
        "score": score,
        "ok": True,
        "note": "ptg ptg_bandit",
    }


def ptg_jailbreak(*, detect: bool) -> dict[str, Any]:
    """Flag jailbreak-detection use case (report-only)."""
    return {
        "detect": detect,
        "apply": False,
        "ok": True,
        "note": "ptg ptg_jailbreak",
    }


def ptg_loop_plan(*, phase: str) -> dict[str, Any]:
    """Gradient → edit → beam → bandit."""
    order = ("gradient", "edit", "beam", "bandit")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "gradient"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "ptg ptg_loop_plan",
    }
