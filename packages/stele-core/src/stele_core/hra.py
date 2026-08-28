"""HRA proxies (stdlib; no LLM).

Shaped by HRA (arXiv:2405.17484): Householder reflections sit
between LoRA and orthogonal adapters. Proxies only.

Prefix ``hra_*`` — not HiRA (``hir_*``) / OFT (``oft_*``) /
OLoRA (``olr_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def hra_house(*, task: str, n: int) -> dict[str, Any]:
    """Allocate n Householder vectors (n >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if n < 1:
        raise SchemaError("n must be >= 1")
    hid = hashlib.sha256(
        canonical_dumps({"t": t, "n": n}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "house_id": hid,
        "n": n,
        "ok": True,
        "note": "hra hra_house",
    }


def hra_reflect(*, house_id: str) -> dict[str, Any]:
    """Compose Householder reflections."""
    hid = house_id.strip()
    if not hid:
        raise SchemaError("house_id required")
    rid = hashlib.sha256(
        canonical_dumps({"h": hid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "reflect_id": rid,
        "ok": True,
        "note": "hra hra_reflect",
    }


def hra_train(*, reflect_id: str) -> dict[str, Any]:
    """Train the reflection adapter."""
    rid = reflect_id.strip()
    if not rid:
        raise SchemaError("reflect_id required")
    tid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "hra hra_train",
    }


def hra_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score HRA run (0–100)."""
    tid = train_id.strip()
    if not tid:
        raise SchemaError("train_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"t": tid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "hra hra_score",
    }


def hra_ortho(*, ortho_stable: bool) -> dict[str, Any]:
    """Flag orthogonal-stable updates (report-only)."""
    return {
        "ortho_stable": ortho_stable,
        "apply": False,
        "ok": True,
        "note": "hra hra_ortho",
    }


def hra_loop_plan(*, phase: str) -> dict[str, Any]:
    """House → reflect → train → score."""
    order = ("house", "reflect", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "house"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "hra hra_loop_plan",
    }
