"""ATTEMPT proxies (stdlib; no LLM).

Shaped by ATTEMPT (arXiv:2205.11961): attentional mixtures of source
soft prompts with a target prompt; LM frozen. Proxies only.

Prefix ``atm_*`` — not Soft Prompt Mixtures (``msp_*``) / SPoT (``spot_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def atm_source(*, source_task: str) -> dict[str, Any]:
    """Pre-train / register a source soft prompt for a large-scale task."""
    t = source_task.strip()
    if not t:
        raise SchemaError("source_task required")
    sid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "src_id": sid,
        "ok": True,
        "note": "atm atm_source",
    }


def atm_target(*, target_task: str) -> dict[str, Any]:
    """Initialize a new target-task soft prompt."""
    t = target_task.strip()
    if not t:
        raise SchemaError("target_task required")
    tid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "tgt_id": tid,
        "ok": True,
        "note": "atm atm_target",
    }


def atm_attend(*, src_id: str, tgt_id: str) -> dict[str, Any]:
    """Compute attention weights over source + target prompts for an instance."""
    sid = src_id.strip()
    tid = tgt_id.strip()
    if not sid or not tid:
        raise SchemaError("src_id and tgt_id required")
    aid = hashlib.sha256(
        canonical_dumps({"s": sid, "t": tid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "attn_id": aid,
        "ok": True,
        "note": "atm atm_attend",
    }


def atm_mix(*, attn_id: str, score: int) -> dict[str, Any]:
    """Interpolate source/target into an instance-wise prompt (score 0–100)."""
    aid = attn_id.strip()
    if not aid:
        raise SchemaError("attn_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    mid = hashlib.sha256(
        canonical_dumps({"a": aid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "mix_id": mid,
        "score": score,
        "ok": True,
        "note": "atm atm_mix",
    }


def atm_modular(*, modular: bool) -> dict[str, Any]:
    """Flag modular add/remove of source prompts (report-only)."""
    return {
        "modular": modular,
        "apply": False,
        "ok": True,
        "note": "atm atm_modular",
    }


def atm_loop_plan(*, phase: str) -> dict[str, Any]:
    """Source → target → attend → mix."""
    order = ("source", "target", "attend", "mix")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "source"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "atm atm_loop_plan",
    }
