"""Prefix-Tuning proxies (stdlib; no LLM).

Shaped by Prefix-Tuning (arXiv:2101.00190): optimize continuous
task-specific prefix vectors for generation while freezing the LM.
Proxies only.

Prefix ``pfx_*`` — not AutoPrompt (``aup_*``) / P-Tuning.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def pfx_task(*, task: str) -> dict[str, Any]:
    """Register a generation task for a shared continuous prefix."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    tid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "task_id": tid,
        "ok": True,
        "note": "pfx pfx_task",
    }


def pfx_prefix(*, task_id: str) -> dict[str, Any]:
    """Allocate continuous prefix parameters for the task."""
    tid = task_id.strip()
    if not tid:
        raise SchemaError("task_id required")
    pid = hashlib.sha256(
        canonical_dumps({"t": tid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "prefix_id": pid,
        "ok": True,
        "note": "pfx pfx_prefix",
    }


def pfx_optimize(*, prefix_id: str) -> dict[str, Any]:
    """Optimize continuous prefix vectors (LM frozen)."""
    pid = prefix_id.strip()
    if not pid:
        raise SchemaError("prefix_id required")
    oid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "opt_id": oid,
        "ok": True,
        "note": "pfx pfx_optimize",
    }


def pfx_generate(*, opt_id: str, score: int) -> dict[str, Any]:
    """Evaluate generation quality under the optimized prefix (0–100)."""
    oid = opt_id.strip()
    if not oid:
        raise SchemaError("opt_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    gid = hashlib.sha256(
        canonical_dumps({"o": oid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "gen_id": gid,
        "score": score,
        "ok": True,
        "note": "pfx pfx_generate",
    }


def pfx_freeze(*, freeze_lm: bool) -> dict[str, Any]:
    """Flag frozen-LM / prefix-only training (report-only)."""
    return {
        "freeze_lm": freeze_lm,
        "apply": False,
        "ok": True,
        "note": "pfx pfx_freeze",
    }


def pfx_loop_plan(*, phase: str) -> dict[str, Any]:
    """Task → prefix → optimize → generate."""
    order = ("task", "prefix", "optimize", "generate")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "task"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "pfx pfx_loop_plan",
    }
