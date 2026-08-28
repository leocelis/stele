"""LoHa proxies (stdlib; no LLM).

Shaped by LoHa (arXiv:2108.06098): approximate ΔW via Hadamard (element-wise)
product of two low-rank products — four matrices, more expressivity at a
given parameter budget. Proxies only.

Prefix ``lha_*`` — not LoKr (``lkr_*``) / LoRA / FourierFT (``fft_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lha_pair(*, task: str, rank: int) -> dict[str, Any]:
    """Declare two low-rank pairs for Hadamard product (rank >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    pid = hashlib.sha256(
        canonical_dumps({"t": t, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "pair_id": pid,
        "rank": rank,
        "ok": True,
        "note": "lha lha_pair",
    }


def lha_hadamard(*, pair_id: str) -> dict[str, Any]:
    """Form Hadamard product of the two low-rank products."""
    pid = pair_id.strip()
    if not pid:
        raise SchemaError("pair_id required")
    hid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "hadamard_id": hid,
        "ok": True,
        "note": "lha lha_hadamard",
    }


def lha_train(*, hadamard_id: str) -> dict[str, Any]:
    """Train the four LoHa matrices."""
    hid = hadamard_id.strip()
    if not hid:
        raise SchemaError("hadamard_id required")
    tid = hashlib.sha256(
        canonical_dumps({"h": hid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "lha lha_train",
    }


def lha_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score LoHa adaptation (0–100)."""
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
        "note": "lha lha_score",
    }


def lha_express(*, more_expressivity: bool) -> dict[str, Any]:
    """Flag higher expressivity vs LoRA at similar budget (report-only)."""
    return {
        "more_expressivity": more_expressivity,
        "apply": False,
        "ok": True,
        "note": "lha lha_express",
    }


def lha_loop_plan(*, phase: str) -> dict[str, Any]:
    """Pair → hadamard → train → score."""
    order = ("pair", "hadamard", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "pair"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lha lha_loop_plan",
    }
