"""Compacter proxies (stdlib; no LLM).

Shaped by Compacter (arXiv:2106.04647): hypercomplex / Kronecker-parameterized
adapter bottlenecks — far fewer params than Houlsby adapters. Proxies only.

Prefix ``cmp_*`` — not LoRA (``lora_*``) / AdapterFusion (``adf_*``) / (IA)^3.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def cmp_insert(*, task: str) -> dict[str, Any]:
    """Insert task Compacter adapters after attention / FFN blocks."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    iid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "adapter_id": iid,
        "ok": True,
        "note": "cmp cmp_insert",
    }


def cmp_kronecker(*, adapter_id: str, n: int) -> dict[str, Any]:
    """Parameterize adapter via hypercomplex / Kronecker factors (n>=1)."""
    aid = adapter_id.strip()
    if not aid:
        raise SchemaError("adapter_id required")
    if n < 1:
        raise SchemaError("n must be >= 1")
    kid = hashlib.sha256(
        canonical_dumps({"a": aid, "n": n}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "kron_id": kid,
        "n": n,
        "ok": True,
        "note": "cmp cmp_kronecker",
    }


def cmp_train(*, kron_id: str) -> dict[str, Any]:
    """Train Compacter + LayerNorm only; freeze the rest."""
    kid = kron_id.strip()
    if not kid:
        raise SchemaError("kron_id required")
    tid = hashlib.sha256(
        canonical_dumps({"k": kid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "cmp cmp_train",
    }


def cmp_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score Compacter adaptation (0–100)."""
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
        "note": "cmp cmp_score",
    }


def cmp_compact(*, param_efficient: bool) -> dict[str, Any]:
    """Flag extreme parameter efficiency vs Houlsby adapters (report-only)."""
    return {
        "param_efficient": param_efficient,
        "apply": False,
        "ok": True,
        "note": "cmp cmp_compact",
    }


def cmp_loop_plan(*, phase: str) -> dict[str, Any]:
    """Insert → kronecker → train → score."""
    order = ("insert", "kronecker", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "insert"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "cmp cmp_loop_plan",
    }
