"""BoHA proxies (stdlib; no LLM).

Shaped by BoHA (arXiv:2509.21637): blockwise Hadamard modulation of
frozen W0 — local rank lift vs global HiRA. Proxies only.

Prefix ``bha_*`` — not LoHA (``lha_*``) / ABBA (``abb_*``) / SMoA
(``smo_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def bha_split(*, task: str, blocks: int) -> dict[str, Any]:
    """Partition W into blocks (blocks >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if blocks < 1:
        raise SchemaError("blocks must be >= 1")
    sid = hashlib.sha256(
        canonical_dumps({"t": t, "b": blocks}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "split_id": sid,
        "blocks": blocks,
        "ok": True,
        "note": "bha bha_split",
    }


def bha_hadamard(*, split_id: str) -> dict[str, Any]:
    """Per-block W_ij ⊙ (B_ij A_ij)."""
    sid = split_id.strip()
    if not sid:
        raise SchemaError("split_id required")
    hid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "hadamard_id": hid,
        "ok": True,
        "note": "bha bha_hadamard",
    }


def bha_train(*, hadamard_id: str) -> dict[str, Any]:
    """Train block adapters."""
    hid = hadamard_id.strip()
    if not hid:
        raise SchemaError("hadamard_id required")
    tid = hashlib.sha256(
        canonical_dumps({"h": hid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "bha bha_train",
    }


def bha_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score BoHA run (0–100)."""
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
        "note": "bha bha_score",
    }


def bha_local(*, localized: bool) -> dict[str, Any]:
    """Flag localized rank lift (report-only)."""
    return {
        "localized": localized,
        "apply": False,
        "ok": True,
        "note": "bha bha_local",
    }


def bha_loop_plan(*, phase: str) -> dict[str, Any]:
    """Split → hadamard → train → score."""
    order = ("split", "hadamard", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "split"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "bha bha_loop_plan",
    }
