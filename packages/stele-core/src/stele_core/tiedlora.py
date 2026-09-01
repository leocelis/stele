"""Tied-LoRA proxies (stdlib; no LLM).

Shaped by Tied-LoRA (arXiv:2311.09578): share low-rank weights across
layers and selectively train. Two prefixes:

- ``tlo_*`` — original v14.2 surface (base → tie → train → score)
- ``tld_*`` — v17.8 surface (tie → select → scale → score)

Not VeRA (``vra_*``) / NOLA (``nla_*``) / QA-LoRA (``qal_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def tlo_base(*, task: str, rank: int) -> dict[str, Any]:
    """Allocate a Tied-LoRA base (rank >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    bid = hashlib.sha256(
        canonical_dumps({"t": t, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "base_id": bid,
        "rank": rank,
        "ok": True,
        "note": "tlo tlo_base",
    }


def tlo_tie(*, base_id: str, layers: int) -> dict[str, Any]:
    """Tie A/B across layers (layers >= 1)."""
    bid = base_id.strip()
    if not bid:
        raise SchemaError("base_id required")
    if layers < 1:
        raise SchemaError("layers must be >= 1")
    tid = hashlib.sha256(
        canonical_dumps({"b": bid, "l": layers}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "tie_id": tid,
        "layers": layers,
        "ok": True,
        "note": "tlo tlo_tie",
    }


def tlo_train(*, tie_id: str) -> dict[str, Any]:
    """Train the tied adapters."""
    tid = tie_id.strip()
    if not tid:
        raise SchemaError("tie_id required")
    rid = hashlib.sha256(
        canonical_dumps({"t": tid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": rid,
        "ok": True,
        "note": "tlo tlo_train",
    }


def tlo_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score Tied-LoRA adaptation (0–100)."""
    tid = train_id.strip()
    if not tid:
        raise SchemaError("train_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"t": tid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "tlo tlo_score",
    }


def tlo_efficient(*, weight_tied: bool) -> dict[str, Any]:
    """Flag weight tying (report-only)."""
    return {
        "weight_tied": weight_tied,
        "apply": False,
        "ok": True,
        "note": "tlo tlo_efficient",
    }


def tlo_loop_plan(*, phase: str) -> dict[str, Any]:
    """Base → tie → train → score."""
    order = ("base", "tie", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "base"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "tlo tlo_loop_plan",
    }


def tld_tie(*, task: str, layers: int) -> dict[str, Any]:
    """Tie A/B across layers (layers >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if layers < 1:
        raise SchemaError("layers must be >= 1")
    tid = hashlib.sha256(
        canonical_dumps({"t": t, "l": layers}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "tie_id": tid,
        "layers": layers,
        "ok": True,
        "note": "tld tld_tie",
    }


def tld_select(*, tie_id: str) -> dict[str, Any]:
    """Select which tied factors train vs freeze."""
    tid = tie_id.strip()
    if not tid:
        raise SchemaError("tie_id required")
    sid = hashlib.sha256(
        canonical_dumps({"t": tid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "select_id": sid,
        "ok": True,
        "note": "tld tld_select",
    }


def tld_scale(*, select_id: str) -> dict[str, Any]:
    """Train per-layer scaling vectors."""
    sid = select_id.strip()
    if not sid:
        raise SchemaError("select_id required")
    kid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "scale_id": kid,
        "ok": True,
        "note": "tld tld_scale",
    }


def tld_score(*, scale_id: str, score: int) -> dict[str, Any]:
    """Score Tied-LoRA v17.8 run (0–100)."""
    sid = scale_id.strip()
    if not sid:
        raise SchemaError("scale_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"s": sid, "v": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "tld tld_score",
    }


def tld_frac(*, fraction_of_lora: bool) -> dict[str, Any]:
    """Flag LoRA-comparable quality at a fraction of params (report-only)."""
    return {
        "fraction_of_lora": fraction_of_lora,
        "apply": False,
        "ok": True,
        "note": "tld tld_frac",
    }


def tld_loop_plan(*, phase: str) -> dict[str, Any]:
    """Tie → select → scale → score."""
    order = ("tie", "select", "scale", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "tie"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "tld tld_loop_plan",
    }
