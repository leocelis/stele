"""LoRA-Flow proxies (stdlib; no LLM).

Shaped by LoRA-Flow (arXiv:2402.11455): token-level fusion gate over
several LoRAs during generation; tiny gate, ~200-shot. Proxies only.

Prefix ``lfw_*`` — not FLoRA (``flo_*``) / S-LoRA (``slr_*``) /
Q-GaLore (``qga_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lfw_pool(*, task: str, n_loras: int) -> dict[str, Any]:
    """Register a LoRA skill pool (n_loras >= 2)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if n_loras < 2:
        raise SchemaError("n_loras must be >= 2")
    pid = hashlib.sha256(
        canonical_dumps({"t": t, "n": n_loras}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "pool_id": pid,
        "n_loras": n_loras,
        "ok": True,
        "note": "lfw lfw_pool",
    }


def lfw_gate(*, pool_id: str) -> dict[str, Any]:
    """Attach the tiny fusion gate (~0.2% of one LoRA)."""
    pid = pool_id.strip()
    if not pid:
        raise SchemaError("pool_id required")
    gid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "gate_id": gid,
        "ok": True,
        "note": "lfw lfw_gate",
    }


def lfw_token(*, gate_id: str) -> dict[str, Any]:
    """Emit token-level fusion weights from the prefix."""
    gid = gate_id.strip()
    if not gid:
        raise SchemaError("gate_id required")
    tid = hashlib.sha256(
        canonical_dumps({"g": gid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "token_id": tid,
        "ok": True,
        "note": "lfw lfw_token",
    }


def lfw_score(*, token_id: str, score: int) -> dict[str, Any]:
    """Score LoRA-Flow run (0–100)."""
    tid = token_id.strip()
    if not tid:
        raise SchemaError("token_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"t": tid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "lfw lfw_score",
    }


def lfw_few(*, few_shot: bool) -> dict[str, Any]:
    """Flag ~200-example gate training (report-only)."""
    return {
        "few_shot": few_shot,
        "apply": False,
        "ok": True,
        "note": "lfw lfw_few",
    }


def lfw_loop_plan(*, phase: str) -> dict[str, Any]:
    """Pool → gate → token → score."""
    order = ("pool", "gate", "token", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "pool"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lfw lfw_loop_plan",
    }
